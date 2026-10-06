import os
from dotenv import load_dotenv
from pymongo import MongoClient


# ============================================================
# 1. MONGODB CONNECTION
# ============================================================

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI was not found. Check your .env file.")

client = MongoClient(MONGODB_URI)

db = client["insurance_company"]
collection = db["insurance_data"]

print("Connected to MongoDB successfully.")


# ============================================================
# 2. INPUT VALIDATION FUNCTIONS
# ============================================================

def get_required_input(message):
    """Return non-empty text input."""
    while True:
        value = input(message).strip()

        if value == "":
            print("This field cannot be empty. Enter NONE if unavailable.")
        else:
            return value


def get_positive_integer(message, allow_none=True):
    """Validate a non-negative integer and return it as text, or None."""
    while True:
        value = input(message).strip()

        if allow_none and value.upper() == "NONE":
            return None

        try:
            number = int(value)

            if number < 0:
                print("Value cannot be negative.")
            else:
                return str(number)

        except ValueError:
            print("Please enter a valid integer or NONE.")


def get_positive_float(message, allow_none=True):
    """Validate a non-negative number and return it as text, or None."""
    while True:
        value = input(message).strip()

        if allow_none and value.upper() == "NONE":
            return None

        try:
            number = float(value)

            if number < 0:
                print("Value cannot be negative.")
            else:
                return str(number)

        except ValueError:
            print("Please enter a valid number or NONE.")


def get_yes_no(message, allow_none=True):
    """Return Y, N, or None."""
    while True:
        value = input(message).strip().upper()

        if allow_none and value == "NONE":
            return None

        if value in ("Y", "N"):
            return value

        if allow_none:
            print("Please enter Y, N, or NONE.")
        else:
            print("Please enter Y or N.")


def get_incident_hour():
    """Return an incident hour from 0 through 23 or None."""
    while True:
        value = input("Incident Hour (0-23): ").strip()

        if value.upper() == "NONE":
            return None

        try:
            hour = int(value)

            if 0 <= hour <= 23:
                return hour

            print("Incident hour must be between 0 and 23.")

        except ValueError:
            print("Please enter a valid hour or NONE.")


# ============================================================
# 3. CREATE - REGISTER A NEW CLAIM
# ============================================================

def create_claim(collection):
    print("\n" + "=" * 50)
    print("              REGISTER NEW CLAIM")
    print("=" * 50)

    print("\n--- POLICY DETAILS ---")

    months_as_customer = get_positive_integer(
        "Months as Customer: "
    )

    age = get_positive_integer("Age: ")

    policy_number = get_required_input("Policy Number: ")

    if policy_number.upper() == "NONE":
        print("Policy Number cannot be NONE.")
        return

    if collection.find_one({"policy_number": policy_number}):
        print("\nA claim with this policy number already exists.")
        return

    policy_bind_date = get_required_input(
        "Policy Bind Date (YYYY-MM-DD): "
    )

    policy_state = get_required_input("Policy State: ")
    policy_csl = get_required_input("Policy CSL: ")

    policy_deductable = get_positive_float(
        "Policy Deductable: "
    )

    policy_annual_premium = get_positive_float(
        "Policy Annual Premium: "
    )

    umbrella_limit = get_positive_integer(
        "Umbrella Limit: "
    )

    insured_zip = get_positive_integer(
        "Insured ZIP: "
    )

    print("\n--- INSURED DETAILS ---")

    insured_sex = get_required_input("Insured Sex: ")
    insured_education_level = get_required_input(
        "Insured Education Level: "
    )
    insured_occupation = get_required_input(
        "Insured Occupation: "
    )
    insured_hobbies = get_required_input(
        "Insured Hobbies: "
    )
    insured_relationship = get_required_input(
        "Insured Relationship: "
    )

    capital_gains = get_positive_integer("Capital Gains: ")
    capital_loss = get_positive_integer("Capital Loss: ")

    print("\n--- INCIDENT DETAILS ---")

    incident_date = get_required_input(
        "Incident Date (YYYY-MM-DD): "
    )

    incident_type = get_required_input("Incident Type: ")
    collision_type = get_required_input("Collision Type: ")
    incident_severity = get_required_input(
        "Incident Severity: "
    )
    authorities_contacted = get_required_input(
        "Authorities Contacted: "
    )
    incident_state = get_required_input("Incident State: ")
    incident_city = get_required_input("Incident City: ")
    incident_location = get_required_input(
        "Incident Location: "
    )

    incident_hour_of_the_day = get_incident_hour()

    number_of_vehicles_involved = get_positive_integer(
        "Number of Vehicles Involved: "
    )

    print("\n--- DAMAGE / EVIDENCE DETAILS ---")

    property_damage = get_yes_no(
        "Property Damage (Y/N/NONE): "
    )

    bodily_injuries = get_positive_integer(
        "Bodily Injuries: "
    )

    witnesses = get_positive_integer(
        "Witnesses: "
    )

    police_report_available = get_yes_no(
        "Police Report Available (Y/N/NONE): "
    )

    print("\n--- CLAIM DETAILS ---")

    total_claim_amount = get_positive_float(
        "Total Claim Amount: "
    )

    injury_claim = get_positive_float(
        "Injury Claim: "
    )

    property_claim = get_positive_float(
        "Property Claim: "
    )

    vehicle_claim = get_positive_float(
        "Vehicle Claim: "
    )

    if (
        total_claim_amount is not None
        and injury_claim is not None
        and property_claim is not None
        and vehicle_claim is not None
    ):
        component_total = (
            float(injury_claim)
            + float(property_claim)
            + float(vehicle_claim)
        )

        if abs(component_total - float(total_claim_amount)) > 0.01:
            print(
                "\nWarning: component claims do not equal "
                "the total claim amount."
            )

            if get_yes_no(
                "Continue registering this claim? (Y/N): ",
                allow_none=False
            ) == "N":
                print("Claim registration cancelled.")
                return
    
    print("\n--- VEHICLE DETAILS ---")

    auto_make = get_required_input("Auto Make: ")
    auto_model = get_required_input("Auto Model: ")

    auto_year = get_positive_integer(
        "Auto Year: "
    )

    print("\n--- HISTORICAL LABEL ---")

    fraud_reported = get_yes_no(
        "Fraud Reported in historical record (Y/N/NONE): "
    )


    claim = {
        "months_as_customer": months_as_customer,
        "age": age,
        "policy_number": policy_number,
        "policy_bind_date": policy_bind_date,
        "policy_state": policy_state,
        "policy_csl": policy_csl,
        "policy_deductable": policy_deductable,
        "policy_annual_premium": policy_annual_premium,
        "umbrella_limit": umbrella_limit,
        "insured_zip": insured_zip,

        "insured_sex": insured_sex,
        "insured_education_level": insured_education_level,
        "insured_occupation": insured_occupation,
        "insured_hobbies": insured_hobbies,
        "insured_relationship": insured_relationship,
        "capital-gains": capital_gains,
        "capital-loss": capital_loss,

        "incident_date": incident_date,
        "incident_type": incident_type,
        "collision_type": collision_type,
        "incident_severity": incident_severity,
        "authorities_contacted": authorities_contacted,
        "incident_state": incident_state,
        "incident_city": incident_city,
        "incident_location": incident_location,
        "incident_hour_of_the_day": incident_hour_of_the_day,
        "number_of_vehicles_involved": number_of_vehicles_involved,

        "property_damage": property_damage,
        "bodily_injuries": bodily_injuries,
        "witnesses": witnesses,
        "police_report_available": police_report_available,

        "total_claim_amount": total_claim_amount,
        "injury_claim": injury_claim,
        "property_claim": property_claim,
        "vehicle_claim": vehicle_claim,

        "auto_make": auto_make,
        "auto_model": auto_model,
        "auto_year": auto_year,
        "fraud_reported": fraud_reported
    }

    try:
        result = collection.insert_one(claim)

        print("\nClaim registered successfully!")
        print("Record ID:", result.inserted_id)

    except Exception as error:
        print("\nUnable to register claim.")
        print("Error:", error)


def display_complete_claim(claim):
    """Display every field of one claim in a readable format."""

    sections = [
        (
            "POLICY DETAILS",
            [
                ("Months as Customer", "months_as_customer"),
                ("Age", "age"),
                ("Policy Number", "policy_number"),
                ("Policy Bind Date", "policy_bind_date"),
                ("Policy State", "policy_state"),
                ("Policy CSL", "policy_csl"),
                ("Policy Deductable", "policy_deductable"),
                ("Policy Annual Premium", "policy_annual_premium"),
                ("Umbrella Limit", "umbrella_limit"),
                ("Insured ZIP", "insured_zip"),
            ],
        ),
        (
            "INSURED DETAILS",
            [
                ("Insured Sex", "insured_sex"),
                ("Insured Education Level", "insured_education_level"),
                ("Insured Occupation", "insured_occupation"),
                ("Insured Hobbies", "insured_hobbies"),
                ("Insured Relationship", "insured_relationship"),
                ("Capital Gains", "capital-gains"),
                ("Capital Loss", "capital-loss"),
            ],
        ),
        (
            "INCIDENT DETAILS",
            [
                ("Incident Date", "incident_date"),
                ("Incident Type", "incident_type"),
                ("Collision Type", "collision_type"),
                ("Incident Severity", "incident_severity"),
                ("Authorities Contacted", "authorities_contacted"),
                ("Incident State", "incident_state"),
                ("Incident City", "incident_city"),
                ("Incident Location", "incident_location"),
                ("Incident Hour of the Day", "incident_hour_of_the_day"),
                ("Number of Vehicles Involved", "number_of_vehicles_involved"),
            ],
        ),
        (
            "DAMAGE / EVIDENCE DETAILS",
            [
                ("Property Damage", "property_damage"),
                ("Bodily Injuries", "bodily_injuries"),
                ("Witnesses", "witnesses"),
                ("Police Report Available", "police_report_available"),
            ],
        ),
        (
            "CLAIM DETAILS",
            [
                ("Total Claim Amount", "total_claim_amount"),
                ("Injury Claim", "injury_claim"),
                ("Property Claim", "property_claim"),
                ("Vehicle Claim", "vehicle_claim"),
            ],
        ),
        (
            "VEHICLE DETAILS",
            [
                ("Auto Make", "auto_make"),
                ("Auto Model", "auto_model"),
                ("Auto Year", "auto_year"),
            ],
        ),
        (
            "HISTORICAL FRAUD LABEL",
            [
                ("Fraud Reported", "fraud_reported"),
            ],
        ),
    ]

    print("\n" + "=" * 60)
    print("                 COMPLETE CLAIM DETAILS")
    print("=" * 60)

    for section_name, fields in sections:
        print(f"\n--- {section_name} ---")

        for label, field_name in fields:
            value = claim.get(field_name)

            if value is None:
                value = "NONE"

            print(f"{label:<30}: {value}")

    print("\n" + "=" * 60)


def _to_number(value):
    """Convert a stored numeric string to a number for comparisons."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# 4. READ - SEARCH CLAIMS
# ============================================================

def search_claims(collection):
    print("\n" + "=" * 50)
    print("                 SEARCH CLAIMS")
    print("=" * 50)

    print("1. Search by Policy Number")
    print("2. Search by Age")
    print("3. Search by Policy State")
    print("4. Search by Fraud Status")
    print("5. Search by Claim Amount Range")
    print("6. Search by Incident Type")
    print("7. Search by Incident State")
    print("8. Search by Vehicle Make")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        policy_number = get_required_input(
            "Enter Policy Number: "
        )

        claim = collection.find_one(
            {"policy_number": policy_number}
        )

        if claim is None:
            print("\nNo claim found for that policy number.")
            return

        display_complete_claim(claim)
        return

    query = {}

    if choice == "2":
        age = get_positive_integer(
            "Enter Age: ",
            allow_none=False
        )

        query = {
            "age": age
        }

    elif choice == "3":
        value = get_required_input(
            "Enter Policy State: "
        )

        query = {
            "policy_state": {
                "$regex": f"^{value}$",
                "$options": "i"
            }
        }

    elif choice == "4":
        fraud_status = get_yes_no(
            "Enter Fraud Status (Y/N): ",
            allow_none=False
        )

        query = {
            "fraud_reported": fraud_status
        }

    elif choice == "5":
        minimum = get_positive_float(
            "Enter minimum claim amount: ",
            allow_none=False
        )

        maximum = get_positive_float(
            "Enter maximum claim amount: ",
            allow_none=False
        )

        minimum_value = float(minimum)
        maximum_value = float(maximum)

        if minimum_value > maximum_value:
            print(
                "Minimum claim amount cannot be greater "
                "than maximum claim amount."
            )
            return

        query = {
            "_numeric_filter": (
                "total_claim_amount",
                minimum_value,
                maximum_value
            )
        }

    elif choice == "6":
        value = get_required_input(
            "Enter Incident Type: "
            )

        query = {
            "incident_type": {
                "$regex": f"^{value}$",
                "$options": "i"
            }
        }

    elif choice == "7":
        value = get_required_input(
            "Enter Incident State: "
        )

        query = {
            "incident_state": {
                "$regex": f"^{value}$",
                "$options": "i"
            }
        }

    elif choice == "8":
        value = get_required_input(
            "Enter Vehicle Make: "
        )

        query = {
            "auto_make": {
                "$regex": f"^{value}$",
                "$options": "i"
            }
        }

    else:
        print("Invalid search choice.")
        return

    try:
        numeric_filter = query.pop("_numeric_filter", None)

        if numeric_filter:
            field, low, high = numeric_filter
            results = (
                claim for claim in collection.find({})
                if claim.get(field) is not None
                and _to_number(claim.get(field)) is not None
                and low <= _to_number(claim.get(field)) <= high
            )
        else:
            numeric_filter = query.pop("_numeric_filter", None)

        if numeric_filter:
            field, low, high = numeric_filter
            base_results = collection.find(query)
            results = (
                claim for claim in base_results
                if claim.get(field) is not None
                and _to_number(claim.get(field)) is not None
                and low <= _to_number(claim.get(field)) <= high
            )
        else:
            results = collection.find(query)

        count = 0

        print("\n" + "=" * 50)
        print("                 SEARCH RESULTS")
        print("=" * 50)

        for claim in results:
            count += 1

            print("\n" + "-" * 45)
            print(
                "Policy Number  :",
                claim.get("policy_number")
            )
            print(
                "Age            :",
                claim.get("age")
            )
            print(
                "Policy State   :",
                claim.get("policy_state")
            )
            print(
                "Incident Type  :",
                claim.get("incident_type")
            )
            print(
                "Incident State :",
                claim.get("incident_state")
            )
            print(
                "Vehicle        :",
                claim.get("auto_make"),
                claim.get("auto_model")
            )
            print(
                "Claim Amount   :",
                claim.get("total_claim_amount")
            )
            print(
                "Fraud Reported :",
                claim.get("fraud_reported")
            )

        if count == 0:
            print("\nNo claims found.")
            return

        print(
            f"\nTotal matching claims: {count}"
        )

        while True:
            detail_policy = input(
                "\nEnter a Policy Number to view ALL details "
                "(or type NONE to return to menu): "
            ).strip()

            if detail_policy.upper() == "NONE":
                return

            detail_claim = collection.find_one(
                {"policy_number": detail_policy}
            )

            if detail_claim is None:
                print("Policy Number not found. Please try again or enter NONE.")
                continue

            display_complete_claim(detail_claim)
            return

    except Exception as error:
        print("\nUnable to search claims.")
        print("Error:", error)


# ============================================================
# 5. UPDATE - UPDATE AN EXISTING CLAIM
# ============================================================

def update_claim(collection):
    print("\n" + "=" * 50)
    print("                 UPDATE CLAIM")
    print("=" * 50)

    policy_number = get_required_input(
        "Enter Policy Number: "
    )

    claim = collection.find_one(
        {"policy_number": policy_number}
    )

    if claim is None:
        print("Claim not found.")
        return

    print("\nClaim found.")

    print("1. Update Policy State")
    print("2. Update Incident Type")
    print("3. Update Incident Severity")
    print("4. Update Total Claim Amount")
    print("5. Update Property Damage")
    print("6. Update Police Report Available")
    print("7. Update Vehicle Make")
    print("8. Update Vehicle Model")
    print("9. Update Incident City")
    print("10. Update Incident State")
    print("11. Update Vehicle Year")
    print("12. Cancel")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    field = None
    value = None

    if choice == "1":
        field = "policy_state"
        value = get_required_input(
            "Enter new Policy State: "
        )

    elif choice == "2":
        field = "incident_type"
        value = get_required_input(
            "Enter new Incident Type: "
        )

    elif choice == "3":
        field = "incident_severity"
        value = get_required_input(
            "Enter new Incident Severity: "
        )

    elif choice == "4":
        field = "total_claim_amount"
        value = get_positive_float(
            "Enter new Total Claim Amount: "
        )

    elif choice == "5":
        field = "property_damage"
        value = get_yes_no(
            "Enter new Property Damage (Y/N/NONE): "
        )

    elif choice == "6":
        field = "police_report_available"
        value = get_yes_no(
            "Enter new Police Report Available (Y/N/NONE): "
        )

    elif choice == "7":
        field = "auto_make"
        value = get_required_input(
            "Enter new Vehicle Make: "
        )

    elif choice == "8":
        field = "auto_model"
        value = get_required_input(
            "Enter new Vehicle Model: "
        )

    elif choice == "9":
        field = "incident_city"
        value = get_required_input(
            "Enter new Incident City: "
        )

    elif choice == "10":
        field = "incident_state"
        value = get_required_input(
            "Enter new Incident State: "
        )

    elif choice == "11":
        field = "auto_year"
        value = get_positive_integer(
            "Enter new Vehicle Year: "
        )

    elif choice == "12":
        print("Update cancelled.")
        return

    else:
        print("Invalid update choice.")
        return

    try:
        result = collection.update_one(
            {"policy_number": policy_number},
            {"$set": {field: value}}
        )

        if result.modified_count == 1:
            print("Claim updated successfully.")
        else:
            print("No changes were made.")

    except Exception as error:
        print("\nUnable to update claim.")
        print("Error:", error)


# ============================================================
# 6. DELETE - DELETE AN EXISTING CLAIM
# ============================================================

def delete_claim(collection):
    print("\n" + "=" * 50)
    print("                 DELETE CLAIM")
    print("=" * 50)

    policy_number = get_required_input(
        "Enter Policy Number: "
    )

    claim = collection.find_one(
        {"policy_number": policy_number}
    )

    if claim is None:
        print("Claim not found.")
        return

    print("\nClaim found.")
    print(
        "Policy Number:",
        claim.get("policy_number")
    )
    print(
        "Incident Type:",
        claim.get("incident_type")
    )
    print(
        "Claim Amount:",
        claim.get("total_claim_amount")
    )

    confirmation = get_yes_no(
        "\nAre you sure you want to delete this claim? (Y/N): ",
        allow_none=False
    )

    if confirmation == "N":
        print("Deletion cancelled.")
        return

    try:
        result = collection.delete_one(
            {"policy_number": policy_number}
        )

        if result.deleted_count == 1:
            print("Claim deleted successfully.")
        else:
            print("Claim could not be deleted.")

    except Exception as error:
        print("\nUnable to delete claim.")
        print("Error:", error)


# ============================================================
# 7. FILTER CLAIMS
# ============================================================

def filter_claims(collection):
    print("\n" + "=" * 50)
    print("                 FILTER CLAIMS")
    print("=" * 50)

    print("1. Claim Amount Range")
    print("2. Age Range")
    print("3. Incident State + Incident Type")
    print("4. Vehicle Make + Minimum Claim Amount")
    print("5. Incident Severity + Minimum Claim Amount")

    choice = input("\nEnter your choice: ").strip()

    query = {}
    numeric_field = None
    minimum_value = None
    maximum_value = None

    if choice == "1":
        minimum = get_positive_float(
            "Enter minimum claim amount: ",
            allow_none=False
        )

        maximum = get_positive_float(
            "Enter maximum claim amount: ",
            allow_none=False
        )

        minimum_value = float(minimum)
        maximum_value = float(maximum)

        if minimum_value > maximum_value:
            print(
                "Minimum amount cannot be greater "
                "than maximum amount."
            )
            return

        numeric_field = "total_claim_amount"

    elif choice == "2":
        minimum = get_positive_integer(
            "Enter minimum age: ",
            allow_none=False
        )

        maximum = get_positive_integer(
            "Enter maximum age: ",
            allow_none=False
        )

        minimum_value = float(minimum)
        maximum_value = float(maximum)

        if minimum_value > maximum_value:
            print(
                "Minimum age cannot be greater "
                "than maximum age."
            )
            return

        numeric_field = "age"

    elif choice == "3":
        state = get_required_input(
            "Enter Incident State: "
        )

        incident_type = get_required_input(
            "Enter Incident Type: "
        )

        query["incident_state"] = {
            "$regex": f"^{state}$",
            "$options": "i"
        }

        query["incident_type"] = {
            "$regex": f"^{incident_type}$",
            "$options": "i"
        }

    elif choice == "4":
        vehicle_make = get_required_input(
            "Enter Vehicle Make: "
        )

        amount = get_positive_float(
            "Enter minimum claim amount: ",
            allow_none=False
        )

        query["auto_make"] = {
            "$regex": f"^{vehicle_make}$",
            "$options": "i"
        }

        numeric_field = "total_claim_amount"
        minimum_value = float(amount)
        maximum_value = float("inf")

    elif choice == "5":
        severity = get_required_input(
            "Enter Incident Severity: "
        )

        amount = get_positive_float(
            "Enter minimum claim amount: ",
            allow_none=False
        )

        query["incident_severity"] = {
            "$regex": f"^{severity}$",
            "$options": "i"
        }

        numeric_field = "total_claim_amount"
        minimum_value = float(amount)
        maximum_value = float("inf")

    else:
        print("Invalid filter choice.")
        return

    try:
        mongo_results = collection.find(query)

        matching_claims = []

        if numeric_field is not None:
            for claim in mongo_results:
                stored_value = claim.get(
                    numeric_field
                )

                if stored_value is None:
                    continue

                try:

                    numeric_value = float(
                        str(stored_value).strip()
                    )

                except (ValueError, TypeError):
                    continue

                if (
                    minimum_value
                    <= numeric_value
                    <= maximum_value
                ):

                    matching_claims.append(claim)

        else:

            matching_claims = list(mongo_results)

        count = 0

        print("\n" + "=" * 50)
        print("                 FILTER RESULTS")
        print("=" * 50)

        for claim in matching_claims:

            count += 1

            print("\n" + "-" * 45)

            print(
                "Result Number   :",
                count
            )

            print(
                "Policy Number   :",
                claim.get("policy_number")
            )

            print(
                "Age             :",
                claim.get("age")
            )

            print(
                "Incident State  :",
                claim.get("incident_state")
            )

            print(
                "Incident Type   :",
                claim.get("incident_type")
            )

            print(
                "Incident Severity:",
                claim.get("incident_severity")
            )

            print(
                "Vehicle         :",
                claim.get("auto_make"),
                claim.get("auto_model")
            )

            print(
                "Claim Amount    :",
                claim.get("total_claim_amount")
            )

            print(
                "Fraud Reported  :",
                claim.get("fraud_reported")
            )

        if count == 0:
            print("\nNo matching claims found.")

        else:
            print(
                "\nTotal matching claims:",
                count
            )

            while True:
                policy_number = input(
                    "\nEnter a Policy Number to view "
                    "ALL details "
                    "(or type NONE to return to menu): "
                ).strip()

                if policy_number.upper() == "NONE":
                    return

                selected_claim = collection.find_one(
                    {
                        "policy_number":
                        policy_number
                    }
                )

                if selected_claim is None:

                    print(
                        "Policy Number not found. "
                        "Please try again or enter NONE."
                    )

                else:

                    display_complete_claim(
                        selected_claim
                    )
                    return

    except Exception as error:

        print("\nUnable to filter claims.")
        print("Error:", error)


# ============================================================
# 8. MAIN APPLICATION MENU
# ============================================================

def main():
    while True:
        print("\n" + "=" * 50)
        print("       INSURANCE CLAIM MANAGEMENT SYSTEM")
        print("=" * 50)

        print("1. Register New Claim")
        print("2. Search Claims")
        print("3. Update Claim")
        print("4. Delete Claim")
        print("5. Filter Claims")
        print("6. Exit")

        print("=" * 50)

        choice = input(
            "Enter your choice (1-6): "
        ).strip()

        if choice == "1":
            create_claim(collection)

        elif choice == "2":
            search_claims(collection)

        elif choice == "3":
            update_claim(collection)

        elif choice == "4":
            delete_claim(collection)

        elif choice == "5":
            filter_claims(collection)

        elif choice == "6":
            print("\nThank you for using the system.")
            print("Application closed.")
            break

        else:
            print(
                "\nInvalid choice. "
                "Please enter a number from 1 to 6."
            )


if __name__ == "__main__":
    main()