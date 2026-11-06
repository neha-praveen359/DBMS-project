import os
import re
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError

from indexing import _get_execution_stats
from AI import generate_query, execute_search
from analytics import (
    claims_by_incident_type,
    claims_by_incident_state,
    fraud_vs_nonfraud,
    claims_by_vehicle_make,
    claims_by_vehicle_model,
    claims_by_vehicle_year,
)
from statistics import claim_amount_statistics

# ============================================================
# 1. APPLICATION / MONGODB CONNECTION
# ============================================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI was not found. Create a .env file with MONGODB_URI=...")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client["insurance_company"]
collection = db["insurance_data"]


# ============================================================
# 2. FIELD DEFINITIONS / FORM STRUCTURE
# ============================================================

TEXT_FIELDS = [
    "policy_number", "policy_bind_date", "policy_state", "policy_csl",
    "insured_sex", "insured_education_level", "insured_occupation",
    "insured_hobbies", "insured_relationship", "incident_date",
    "incident_type", "collision_type", "incident_severity",
    "authorities_contacted", "incident_state", "incident_city",
    "incident_location", "property_damage", "police_report_available",
    "fraud_reported", "auto_make", "auto_model",
]

INTEGER_FIELDS = [
    "months_as_customer", "age", "umbrella_limit", "insured_zip",
    "capital-gains", "capital-loss", "incident_hour_of_the_day",
    "number_of_vehicles_involved", "bodily_injuries", "witnesses", "auto_year",
]

FLOAT_FIELDS = [
    "policy_deductable", "policy_annual_premium", "total_claim_amount",
    "injury_claim", "property_claim", "vehicle_claim",
]

YES_NO_NONE_FIELDS = ["property_damage", "police_report_available", "fraud_reported"]

FORM_SECTIONS = {
    "Policy Details": [
        ("months_as_customer", "Months as Customer", "number"),
        ("age", "Age", "number"),
        ("policy_number", "Policy Number", "text"),
        ("policy_bind_date", "Policy Bind Date", "date"),
        ("policy_state", "Policy State", "text"),
        ("policy_csl", "Policy CSL", "text"),
        ("policy_deductable", "Policy Deductable", "number"),
        ("policy_annual_premium", "Policy Annual Premium", "number"),
        ("umbrella_limit", "Umbrella Limit", "number"),
        ("insured_zip", "Insured ZIP", "number"),
    ],
    "Insured Details": [
        ("insured_sex", "Insured Sex", "text"),
        ("insured_education_level", "Education Level", "text"),
        ("insured_occupation", "Occupation", "text"),
        ("insured_hobbies", "Hobbies", "text"),
        ("insured_relationship", "Relationship", "text"),
        ("capital-gains", "Capital Gains", "number"),
        ("capital-loss", "Capital Loss", "number"),
    ],
    "Incident Details": [
        ("incident_date", "Incident Date", "date"),
        ("incident_type", "Incident Type", "text"),
        ("collision_type", "Collision Type", "text"),
        ("incident_severity", "Incident Severity", "text"),
        ("authorities_contacted", "Authorities Contacted", "text"),
        ("incident_state", "Incident State", "text"),
        ("incident_city", "Incident City", "text"),
        ("incident_location", "Incident Location", "text"),
        ("incident_hour_of_the_day", "Incident Hour (0–23)", "number"),
        ("number_of_vehicles_involved", "Vehicles Involved", "number"),
    ],
    "Damage & Evidence": [
        ("property_damage", "Property Damage", "select"),
        ("bodily_injuries", "Bodily Injuries", "number"),
        ("witnesses", "Witnesses", "number"),
        ("police_report_available", "Police Report Available", "select"),
    ],
    "Claim Details": [
        ("total_claim_amount", "Total Claim Amount", "number"),
        ("injury_claim", "Injury Claim", "number"),
        ("property_claim", "Property Claim", "number"),
        ("vehicle_claim", "Vehicle Claim", "number"),
    ],
    "Vehicle Details": [
        ("auto_make", "Auto Make", "text"),
        ("auto_model", "Auto Model", "text"),
        ("auto_year", "Auto Year", "number"),
    ],
    "Historical Information": [
        ("fraud_reported", "Fraud Reported", "select"),
    ],
}

SEARCH_FIELDS = {
    "policy_number": "Policy Number",
    "age": "Age",
    "policy_state": "Policy State",
    "fraud_reported": "Fraud Status",
    "incident_type": "Incident Type",
    "incident_state": "Incident State",
    "auto_make": "Vehicle Make",
}


# ============================================================
# 3. VALIDATION / CONVERSION FUNCTIONS
# ============================================================

def clean_value(field, raw, allow_none=True):
    """Validate one browser form value using the original CLI rules."""
    value = (raw or "").strip()

    if allow_none and value == "":
        return None

    if field in INTEGER_FIELDS:
        try:
            number = int(value)
            if number < 0:
                raise ValueError
            if field == "incident_hour_of_the_day" and number > 23:
                raise ValueError
            return str(number)
        except ValueError:
            raise ValueError(
                f"{field.replace('_', ' ').title()} must be a valid non-negative integer."
            )

    if field in FLOAT_FIELDS:
        try:
            number = float(value)
            if number < 0:
                raise ValueError
            return str(number)
        except ValueError:
            raise ValueError(
                f"{field.replace('_', ' ').title()} must be a valid non-negative number."
            )

    if field in YES_NO_NONE_FIELDS:
        value = value.upper()
        if value not in {"Y", "N", "NONE"}:
            raise ValueError(f"{field.replace('_', ' ').title()} must be Y, N, or NONE.")
        return None if value == "NONE" else value

    return value


def form_to_claim(form):
    """Convert the complete HTML form into the same claim schema as the CLI app."""
    claim = {}
    for field in TEXT_FIELDS + INTEGER_FIELDS + FLOAT_FIELDS:
        value = clean_value(field, form.get(field, ""))
        if field == "policy_number" and not value:
            raise ValueError("Policy Number cannot be empty.")
        if field in TEXT_FIELDS and field not in YES_NO_NONE_FIELDS and not value:
            raise ValueError(f"{field.replace('_', ' ').title()} cannot be empty.")
        claim[field] = value
    return claim


def _to_number(value):
    """Convert stored numeric strings to float for range comparisons."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_claim_components(claim):
    """Return True when claim components do not equal the total amount."""
    components = [
        claim.get("injury_claim"),
        claim.get("property_claim"),
        claim.get("vehicle_claim"),
    ]
    if claim.get("total_claim_amount") is None or not all(x is not None for x in components):
        return False
    total = sum(float(x) for x in components)
    return abs(total - float(claim["total_claim_amount"])) > 0.01


# ============================================================
# 4. DISPLAY / DATABASE HELPERS
# ============================================================

def claim_display(claim):
    """Prepare a claim for display; convert date strings for HTML date inputs."""
    claim = dict(claim)
    claim["_id"] = str(claim.get("_id", ""))
    for field in ("policy_bind_date", "incident_date"):
        value = claim.get(field)
        if not value:
            continue
        text_value = str(value).strip()
        # HTML <input type=date> only accepts YYYY-MM-DD.
        parsed = None
        for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                parsed = datetime.strptime(text_value, fmt)
                break
            except ValueError:
                pass
        if parsed:
            claim[field] = parsed.strftime("%Y-%m-%d")
    return claim


def preserve_date_storage_format(new_value, old_value):
    """Convert an HTML date value back to the stored date format when possible."""
    if not new_value:
        # An empty date input must not erase an existing date during an edit.
        return old_value
    try:
        parsed = datetime.strptime(str(new_value), "%Y-%m-%d")
    except ValueError:
        return new_value
    old_text = str(old_value or "")
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            datetime.strptime(old_text, fmt)
            return parsed.strftime(fmt)
        except ValueError:
            pass
    return parsed.strftime("%Y-%m-%d")


def get_claim_by_id(claim_id):
    try:
        oid = ObjectId(claim_id)
    except (InvalidId, TypeError):
        return None
    return collection.find_one({"_id": oid})


def claims_display(cursor):
    return [claim_display(x) for x in cursor]


def apply_numeric_range(claims, field, minimum=None, maximum=None):
    """Filter numeric-looking string fields safely in Python."""
    results = []
    for claim in claims:
        number = _to_number(claim.get(field))
        if number is None:
            continue
        if minimum is not None and number < minimum:
            continue
        if maximum is not None and number > maximum:
            continue
        results.append(claim)
    return results


def search_query_for_text(field, value):
    return {field: {"$regex": f"^{value}$", "$options": "i"}}


def get_search_results(search_type, value=None, minimum=None, maximum=None):
    """Implement all eight original search modes."""
    if search_type == "policy_number":
        claim = collection.find_one({"policy_number": value})
        return [] if claim is None else [claim]

    if search_type == "age":
        return list(collection.find({"age": str(int(value))}))

    if search_type in {"policy_state", "fraud_reported", "incident_type", "incident_state", "auto_make"}:
        return list(collection.find(search_query_for_text(search_type, value)))

    if search_type == "claim_amount":
        return apply_numeric_range(collection.find({}), "total_claim_amount", minimum, maximum)

    return []


def parse_query_filters(args):
    """Parse the original filter menu into web query parameters."""
    filters = {
        "incident_state": args.get("incident_state", "").strip(),
        "incident_type": args.get("incident_type", "").strip(),
        "auto_make": args.get("auto_make", "").strip(),
        "incident_severity": args.get("incident_severity", "").strip(),
        "policy_state": args.get("policy_state", "").strip(),
        "fraud_reported": args.get("fraud_reported", "").strip().upper(),
    }
    minimum = args.get("min_amount", "").strip()
    maximum = args.get("max_amount", "").strip()
    min_age = args.get("min_age", "").strip()
    max_age = args.get("max_age", "").strip()

    query = {}
    for field in (
        "policy_state",
        "incident_state",
        "incident_type",
        "auto_make",
        "incident_severity",
    ):
        if filters[field]:
            query[field] = {"$regex": f"^{filters[field]}$", "$options": "i"}

    if filters["fraud_reported"] in {"Y", "N"}:
        query["fraud_reported"] = filters["fraud_reported"]

    min_amount = _safe_float(minimum)
    max_amount = _safe_float(maximum)
    min_age_value = _safe_float(min_age)
    max_age_value = _safe_float(max_age)

    return query, min_amount, max_amount, min_age_value, max_age_value


def _safe_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# 5. CORE CLAIM OPERATIONS (same responsibilities as original CLI)
# ============================================================

def create_claim(db_collection, claim):
    """Create/register a claim. Web route handles form presentation."""
    if not claim.get("policy_number"):
        raise ValueError("Policy Number cannot be empty.")
    if db_collection.find_one({"policy_number": claim["policy_number"]}):
        raise ValueError("A claim with this policy number already exists.")
    return db_collection.insert_one(claim)


def display_complete_claim(claim):
    """Return a complete claim in a web-friendly dictionary."""
    return claim_display(claim)


def search_claims(db_collection, search_type, value=None, minimum=None, maximum=None):
    """Search using the original application's eight search choices."""
    if search_type == "policy_number":
        claim = db_collection.find_one({"policy_number": value})
        return [] if claim is None else [claim]
    if search_type == "age":
        return list(db_collection.find({"age": str(int(value))}))
    if search_type in {"policy_state", "fraud_reported", "incident_type", "incident_state", "auto_make"}:
        return list(db_collection.find(search_query_for_text(search_type, value)))
    if search_type == "claim_amount":
        return apply_numeric_range(db_collection.find({}), "total_claim_amount", minimum, maximum)
    return []


def update_claim(db_collection, claim_id, updated_claim):
    """Update the complete claim document using MongoDB update_one()."""
    claim = get_claim_by_id(claim_id)
    if not claim:
        return None
    if updated_claim.get("policy_number") != claim.get("policy_number") and db_collection.find_one({"policy_number": updated_claim.get("policy_number")}):
        raise ValueError("Another claim already uses that policy number.")
    return db_collection.update_one({"_id": claim["_id"]}, {"$set": updated_claim})


def delete_claim(db_collection, claim_id):
    """Delete one claim after the web layer confirms the user's action."""
    claim = get_claim_by_id(claim_id)
    if not claim:
        return None
    return db_collection.delete_one({"_id": claim["_id"]})


def filter_claims(db_collection, query, min_amount=None, max_amount=None, min_age=None, max_age=None):
    """Apply the original multi-condition filters, including numeric string ranges."""
    claims = list(db_collection.find(query).sort("_id", -1))
    if min_amount is not None or max_amount is not None:
        claims = apply_numeric_range(claims, "total_claim_amount", min_amount, max_amount)
    if min_age is not None or max_age is not None:
        claims = apply_numeric_range(claims, "age", min_age, max_age)
    return claims



# ============================================================
# 5. TEMPLATE HELPERS
# ============================================================

@app.template_filter("money")
def money(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


@app.template_filter("pretty")
def pretty(value):
    if value is None or value == "":
        return "—"
    return str(value)


@app.context_processor
def inject_globals():
    return {
        "now": datetime.now(),
        "form_sections": FORM_SECTIONS,
        "sections": FORM_SECTIONS,
        "search_fields": SEARCH_FIELDS,
        "text_required_fields": {
            field for field in TEXT_FIELDS if field not in YES_NO_NONE_FIELDS
        },
    }


# ============================================================
# 6. DASHBOARD
# ============================================================

@app.route("/")
def dashboard():
    try:
        total = collection.count_documents({})
        fraud = collection.count_documents({"fraud_reported": "Y"})
        nonfraud = collection.count_documents({"fraud_reported": "N"})
        pipeline = [{"$group": {
            "_id": None,
            "total": {"$sum": {"$convert": {"input": "$total_claim_amount", "to": "double", "onError": 0, "onNull": 0}}},
            "avg": {"$avg": {"$convert": {"input": "$total_claim_amount", "to": "double", "onError": None, "onNull": None}}},
        }}]
        amount = next(iter(collection.aggregate(pipeline)), {"total": 0, "avg": 0})
        states = len(collection.distinct("incident_state"))
        makes = len(collection.distinct("auto_make"))
        recent = claims_display(collection.find().sort("_id", -1).limit(6))
        return render_template(
            "dashboard.html", total=total, fraud=fraud, nonfraud=nonfraud,
            total_amount=amount.get("total", 0), avg_amount=amount.get("avg", 0),
            states=states, makes=makes, recent=recent,
        )
    except PyMongoError as error:
        flash(f"Database error: {error}", "error")
        return render_template(
            "dashboard.html", total=0, fraud=0, nonfraud=0,
            total_amount=0, avg_amount=0, states=0, makes=0, recent=[]
        )


# ============================================================
# 7. CREATE / REGISTER CLAIM
# ============================================================

@app.route("/claims/register", methods=["GET", "POST"])
def register_claim():
    if request.method == "POST":
        try:
            claim = form_to_claim(request.form)
            if collection.find_one({"policy_number": claim["policy_number"]}):
                raise ValueError("A claim with this policy number already exists.")

            mismatch = validate_claim_components(claim)
            if mismatch and request.form.get("confirm_mismatch") != "yes":
                flash("The claim components do not equal the total. Check the amounts or confirm to continue.", "warning")
                return render_template("claims/form.html", claim=request.form, editing=False, mismatch=True, sections=FORM_SECTIONS)

            result = create_claim(collection, claim)
            flash(f"Claim registered successfully. Record ID: {result.inserted_id}", "success")
            return redirect(url_for("claim_detail", claim_id=str(result.inserted_id)))
        except (ValueError, DuplicateKeyError, PyMongoError) as error:
            flash(str(error), "error")
            return render_template("claims/form.html", claim=request.form, editing=False, mismatch=False, sections=FORM_SECTIONS)

    return render_template("claims/form.html", claim={}, editing=False, mismatch=False, sections=FORM_SECTIONS)


# ============================================================
# 8. READ / SEARCH CLAIMS
# ============================================================

@app.route("/claims/search")
def search_claims_web():
    """Show all claims by default, or search across common claim fields."""
    q = request.args.get("q", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = 50

    query = {}
    if q:
        escaped_q = re.escape(q)
        searchable_fields = [
            "policy_number", "incident_type", "incident_severity",
            "incident_state", "incident_city", "incident_location",
            "policy_state", "auto_make", "auto_model", "fraud_reported",
        ]
        query = {"$or": [
            {field: {"$regex": escaped_q, "$options": "i"}}
            for field in searchable_fields
        ]}

    try:
        total = collection.count_documents(query)
        pages = max((total + per_page - 1) // per_page, 1)
        if page > pages:
            page = pages
        skip = (page - 1) * per_page
        results = claims_display(
            collection.find(query).sort("_id", -1).skip(skip).limit(per_page)
        )
        return render_template(
            "claims/search.html",
            claims=results,
            q=q,
            page=page,
            pages=pages,
            total=total,
            per_page=per_page,
        )
    except PyMongoError as exc:
        flash(f"Unable to load claims: {exc}", "error")
        return render_template(
            "claims/search.html", claims=[], q=q, page=1, pages=1,
            total=0, per_page=per_page,
        )


@app.route("/claims/<claim_id>")
def claim_detail(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        flash("Claim not found.", "error")
        return redirect(url_for("search_claims_web"))
    return render_template("claims/detail.html", claim=claim_display(claim), sections=FORM_SECTIONS)


# ============================================================
# 9. UPDATE CLAIM
# ============================================================

@app.route("/claims/<claim_id>/edit", methods=["GET", "POST"])
def edit_claim(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        flash("Claim not found.", "error")
        return redirect(url_for("search_claims_web"))

    if request.method == "POST":
        try:
            updated = form_to_claim(request.form)
            # Preserve the existing date if a browser submits a blank date, and
            # retain the date-string format already used by this MongoDB record.
            for date_field in ("policy_bind_date", "incident_date"):
                updated[date_field] = preserve_date_storage_format(
                    request.form.get(date_field, ""), claim.get(date_field)
                )
            if updated["policy_number"] != claim.get("policy_number") and collection.find_one({"policy_number": updated["policy_number"]}):
                raise ValueError("Another claim already uses that policy number.")
            update_claim(collection, claim_id, updated)
            flash("Claim updated successfully.", "success")
            return redirect(url_for("claim_detail", claim_id=claim_id))
        except (ValueError, PyMongoError) as error:
            flash(str(error), "error")
            return render_template("claims/form.html", claim=request.form, editing=True, mismatch=False, claim_id=claim_id, sections=FORM_SECTIONS)

    return render_template("claims/form.html", claim=claim_display(claim), editing=True, mismatch=False, claim_id=claim_id, sections=FORM_SECTIONS)


# ============================================================
# 10. DELETE CLAIM
# ============================================================

@app.post("/claims/<claim_id>/delete")
def delete_claim_web(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        flash("Claim not found.", "error")
    elif request.form.get("confirm") != "yes":
        flash("Deletion was not confirmed.", "warning")
    else:
        try:
            result = delete_claim(collection, claim_id)
            flash(
                "Claim deleted successfully." if result.deleted_count else "Claim could not be deleted.",
                "success" if result.deleted_count else "error",
            )
        except PyMongoError as error:
            flash(f"Unable to delete claim: {error}", "error")
    return redirect(url_for("search_claims_web"))


# ============================================================
# 11. FILTER CLAIMS
# ============================================================

@app.route("/claims/filter")
def filter_claims_web():
    query, min_amount, max_amount, min_age, max_age = parse_query_filters(request.args)
    claims = filter_claims(collection, query, min_amount, max_amount, min_age, max_age)

    # Original application had numeric range filtering because numeric values
    # are stored as strings. Do the conversion safely after MongoDB filtering.
    return render_template("claims/filter.html", claims=claims_display(claims[:500]), filters=request.args)


# ============================================================
# 12. CLAIM AMOUNT STATISTICS / DATA ANALYTICS
# ============================================================

@app.route("/statistics")
def statistics_web():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": None,

                    "claim_count": {
                        "$sum": 1
                    },

                    "total_claim_amount": {
                        "$sum": {
                            "$convert": {
                                "input": "$total_claim_amount",
                                "to": "double",
                                "onError": 0,
                                "onNull": 0
                            }
                        }
                    },

                    "average_claim_amount": {
                        "$avg": {
                            "$convert": {
                                "input": "$total_claim_amount",
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    },

                    "maximum_claim_amount": {
                        "$max": {
                            "$convert": {
                                "input": "$total_claim_amount",
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    },

                    "minimum_claim_amount": {
                        "$min": {
                            "$convert": {
                                "input": "$total_claim_amount",
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    },

                    "std": {
                        "$stdDevPop": {
                            "$convert": {
                                "input": "$total_claim_amount",
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                }
            }
        ]

        result = next(collection.aggregate(pipeline), None)

        if result is None:
            result = {
                "claim_count": 0,
                "total_claim_amount": 0,
                "average_claim_amount": 0,
                "maximum_claim_amount": 0,
                "minimum_claim_amount": 0,
                "std": 0
            }

        maximum = result.get("maximum_claim_amount") or 0
        minimum = result.get("minimum_claim_amount") or 0

        result["range"] = maximum - minimum

        return render_template(
            "statistics.html",
            stats=result
        )

    except Exception as error:
        print("Statistics error:", error)

        stats = {
            "claim_count": 0,
            "total_claim_amount": 0,
            "average_claim_amount": 0,
            "maximum_claim_amount": 0,
            "minimum_claim_amount": 0,
            "range": 0,
            "std": 0
        }

        return render_template(
            "statistics.html",
            stats=stats
        )


@app.route("/analytics")
def analytics_web():
    datasets = {
        "incident_type": claims_by_incident_type(collection),
        "incident_state": claims_by_incident_state(collection),
        "fraud": fraud_vs_nonfraud(collection),
        "vehicle_make": claims_by_vehicle_make(collection),
        "vehicle_model": claims_by_vehicle_model(collection),
        "vehicle_year": claims_by_vehicle_year(collection),
    }
    return render_template("analytics.html", datasets=datasets)


# ============================================================
# 13. INDEXING / QUERY PERFORMANCE
# ============================================================

@app.route("/indexes", methods=["GET", "POST"])
def indexes_web():
    message = None
    if request.method == "POST":
        try:
            collection.create_index([("policy_number", ASCENDING)], name="idx_policy_number")
            collection.create_index([("incident_state", ASCENDING)], name="idx_incident_state")
            collection.create_index([("fraud_reported", ASCENDING)], name="idx_fraud_reported")
            message = "Indexes created/verified successfully."
        except Exception as error:
            message = f"Unable to create indexes: {error}"
    indexes = list(collection.list_indexes())
    return render_template("indexes.html", indexes=indexes, message=message)


@app.route("/performance", methods=["GET", "POST"])
def performance_web():
    result = None
    policy_number = ""
    if request.method == "POST":
        policy_number = request.form.get("policy_number", "").strip()
        if not policy_number:
            flash("Policy number cannot be empty.", "error")
        else:
            try:
                collection.create_index([("policy_number", ASCENDING)], name="idx_policy_number")
                query = {"policy_number": policy_number}
                scan = collection.database.command(
                    "explain", {"find": collection.name, "filter": query, "hint": {"$natural": 1}}, verbosity="executionStats"
                )
                indexed = collection.database.command(
                    "explain", {"find": collection.name, "filter": query, "hint": "idx_policy_number"}, verbosity="executionStats"
                )
                result = {"scan": _get_execution_stats(scan), "indexed": _get_execution_stats(indexed)}
            except Exception as error:
                flash(f"Unable to run performance test: {error}", "error")
    return render_template("performance.html", result=result, policy_number=policy_number)


# ============================================================
# 14. AI NATURAL-LANGUAGE SEARCH
# ============================================================

@app.route("/ai-search", methods=["GET", "POST"])
def ai_search_web():
    results, parsed, query_text = [], None, ""
    if request.method == "POST":
        query_text = request.form.get("query", "").strip()
        if query_text:
            try:
                parsed = generate_query(query_text)
                if parsed:
                    results = claims_display(execute_search(collection, parsed))
                else:
                    flash("I could not understand that search. Try one of the examples shown below.", "warning")
            except Exception as error:
                flash(f"AI search error: {error}", "error")
    return render_template("ai_search.html", results=results, parsed=parsed, query_text=query_text)


# ============================================================
# 15. JSON API HELPERS (OPTIONAL / USEFUL FOR THE WEBSITE)
# ============================================================

@app.get("/api/claims/<claim_id>")
def api_claim(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        return jsonify({"error": "Claim not found"}), 404
    return jsonify(claim_display(claim))


# ============================================================
# 16. ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="The page you requested could not be found."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", code=500, message="Something went wrong while processing your request."), 500


# ============================================================
# 17. APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
