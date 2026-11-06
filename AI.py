import re

# =========================================================
# 1. FIELD MAPPING
# =========================================================

FIELD_KEYWORDS = {

    "policy_number": [
        "policy number",
        "policy no",
        "policy"
    ],

    "age": [
        "age",
        "customer age",
        "aged"
    ],

    "policy_state": [
        "policy state",
        "policy issued in",
        "policy location"
    ],

    "incident_state": [
        "incident state",
        "accident state",
        "incident location state"
    ],

    "incident_city": [
        "incident city",
        "accident city"
    ],

    "incident_type": [
        "incident type",
        "type of incident",
        "accident type"
    ],

    "incident_severity": [
        "incident severity",
        "severity",
        "claim severity"
    ],

    "fraud_reported": [
        "fraud",
        "fraud reported",
        "fraud cases",
        "fraudulent"
    ],

    "total_claim_amount": [
        "total claim amount",
        "claim amount",
        "claims amount",
        "claim value"
    ],

    "injury_claim": [
        "injury claim",
        "injury amount"
    ],

    "property_claim": [
        "property claim",
        "property damage claim"
    ],

    "vehicle_claim": [
        "vehicle claim",
        "vehicle damage claim"
    ],

    "auto_make": [
        "car make",
        "vehicle make",
        "auto make",
        "make"
    ],

    "auto_model": [
        "car model",
        "vehicle model",
        "auto model",
        "model"
    ],

    "auto_year": [
        "car year",
        "vehicle year",
        "auto year",
        "year"
    ],

    "insured_sex": [
        "gender",
        "sex"
    ],

    "authorities_contacted": [
        "authorities contacted",
        "police contacted"
    ],

    "number_of_vehicles_involved": [
        "number of vehicles",
        "vehicles involved"
    ]
}


# =========================================================
# 2. NUMERIC FIELDS
# =========================================================

NUMERIC_FIELDS = {

    "months_as_customer",
    "age",
    "policy_deductable",
    "policy_annual_premium",
    "umbrella_limit",
    "capital-gains",
    "capital-loss",
    "incident_hour_of_the_day",
    "number_of_vehicles_involved",
    "bodily_injuries",
    "witnesses",
    "total_claim_amount",
    "injury_claim",
    "property_claim",
    "vehicle_claim",
    "auto_year"
}


# =========================================================
# 3. NATURAL LANGUAGE PROCESSING
# =========================================================

def normalize_text(text):
    """
    Convert text to lowercase and remove extra spaces.
    """

    return re.sub(
        r"\s+",
        " ",
        text.strip().lower()
    )


def detect_field(query):
    """
    Identify which database field the user is asking about.
    Returns the matching field name or None.
    """

    normalized_query = normalize_text(query)

    all_keywords = []

    for field, keywords in FIELD_KEYWORDS.items():

        for keyword in keywords:

            all_keywords.append(
                (keyword, field)
            )

    # Check longer keywords first
    all_keywords.sort(
        key=lambda item: len(item[0]),
        reverse=True
    )

    for keyword, field in all_keywords:

        if re.search(
            r"\b" + re.escape(keyword) + r"\b",
            normalized_query
        ):

            return field

    return None


def extract_policy_number(query):
    """
    Extract a policy number from the user's request.
    """

    match = re.search(
        r"\b\d{4,}\b",
        query
    )

    if match:
        return match.group(0)

    return None


def extract_number(query):
    """
    Extract the first numeric value from a query.
    """

    match = re.search(
        r"\b\d+(?:\.\d+)?\b",
        query
    )

    if match:
        return float(match.group(0))

    return None


def detect_operator(query):
    """
    Identify whether the user wants an exact match,
    greater-than comparison, or less-than comparison.
    """

    query = normalize_text(query)

    if any(
        word in query
        for word in [
            "above",
            "greater than",
            "more than",
            "over",
            "higher than"
        ]
    ):
        return "$gt"

    if any(
        word in query
        for word in [
            "below",
            "less than",
            "under",
            "lower than"
        ]
    ):
        return "$lt"

    if any(
        word in query
        for word in [
            "at least",
            "minimum",
            "or more"
        ]
    ):
        return "$gte"

    if any(
        word in query
        for word in [
            "at most",
            "maximum",
            "or less"
        ]
    ):
        return "$lte"

    return "$eq"


def extract_text_value(query, field):
    """
    Extract a text value from the query.

    Example:
        Show claims from Ohio

    returns:
        ohio
    """

    normalized_query = normalize_text(query)

    patterns = [
        r"\bfrom\s+(.+)",
        r"\bin\s+(.+)",
        r"\bfor\s+(.+)",
        r"\bmake\s+(.+)",
        r"\bmodel\s+(.+)",
        r"\bstate\s+(.+)",
        r"\btype\s+(.+)",
        r"\bseverity\s+(.+)"
    ]

    value = None

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized_query
        )

        if match:

            value = match.group(1).strip()
            break

    if not value:
        return None

    # Remove common trailing words
    value = re.sub(
        r"\b(claims?|cases?|records?|please|show|me|find|search)\b",
        "",
        value
    ).strip()

    # Remove numbers
    value = re.sub(
        r"\b\d+(?:\.\d+)?\b",
        "",
        value
    ).strip()

    return value if value else None


# =========================================================
# 4. QUERY GENERATION
# =========================================================

def generate_query(user_input):
    """
    Convert a natural-language request into the structure
    expected by execute_search().

    Every successful result contains:

        field
        operator
        value
        query_type
    """

    text = normalize_text(user_input)

    # -----------------------------------------------------
    # POLICY NUMBER
    # -----------------------------------------------------

    if "policy" in text:

        policy_number = extract_policy_number(text)

        if policy_number:

            return {
                "field": "policy_number",
                "operator": "$eq",
                "value": policy_number,
                "query_type": "exact"
            }

    # -----------------------------------------------------
    # AGE
    # -----------------------------------------------------

    if "age" in text or "aged" in text:

        number = extract_number(text)

        if number is not None:

            return {
                "field": "age",
                "operator": "$eq",
                "value": number,
                "query_type": "numeric"
            }

    # -----------------------------------------------------
    # FRAUD
    # -----------------------------------------------------

    if (
        "fraud" in text
        or "fraudulent" in text
    ):

        return {
            "field": "fraud_reported",
            "operator": "$eq",
            "value": "Y",
            "query_type": "exact"
        }

    # -----------------------------------------------------
    # STATE MAPPING
    # -----------------------------------------------------

    # Natural-language state name -> database abbreviation

    state_mapping = {

        "ohio": "OH",
        "indiana": "IN",
        "illinois": "IL",
        "new york": "NY",
        "california": "CA",
        "texas": "TX",
        "arizona": "AZ",
        "virginia": "VA",
        "west virginia": "WV",
        "north carolina": "NC",
        "south carolina": "SC",
        "florida": "FL",
        "georgia": "GA",
        "tennessee": "TN",
        "kentucky": "KY",
        "missouri": "MO",
        "michigan": "MI",
        "minnesota": "MN",
        "wisconsin": "WI",
        "oregon": "OR",
        "washington": "WA",
        "nevada": "NV",
        "utah": "UT",
        "colorado": "CO",
        "pennsylvania": "PA",
        "maryland": "MD",
        "new jersey": "NJ",
        "massachusetts": "MA"
    }

    # -----------------------------------------------------
    # INCIDENT STATE
    # -----------------------------------------------------

    for state_name, state_code in state_mapping.items():

        if state_name in text:

            return {
                "field": "incident_state",
                "operator": "$eq",
                "value": state_code,
                "query_type": "text"
            }

    # -----------------------------------------------------
    # STATE ABBREVIATIONS
    # -----------------------------------------------------

    state_codes = [
        "OH",
        "IN",
        "IL",
        "NY",
        "CA",
        "TX",
        "AZ",
        "VA",
        "WV",
        "NC",
        "SC",
        "FL",
        "GA",
        "TN",
        "KY",
        "MO",
        "MI",
        "MN",
        "WI",
        "OR",
        "WA",
        "NV",
        "UT",
        "CO",
        "PA",
        "MD",
        "NJ",
        "MA"
    ]

    for state_code in state_codes:

        if re.search(
            r"\b" + re.escape(
                state_code.lower()
            ) + r"\b",
            text
        ):

            return {
                "field": "incident_state",
                "operator": "$eq",
                "value": state_code,
                "query_type": "text"
            }

    # -----------------------------------------------------
    # INCIDENT TYPE
    # -----------------------------------------------------

    incident_types = [

        "single vehicle collision",
        "vehicle theft",
        "multi vehicle collision",
        "parked car"
    ]

    for incident_type in incident_types:

        if incident_type in text:

            return {
                "field": "incident_type",
                "operator": "$eq",
                "value": incident_type,
                "query_type": "text"
            }

    # -----------------------------------------------------
    # INCIDENT SEVERITY
    # -----------------------------------------------------

    severities = [

        "trivial damage",
        "minor damage",
        "major damage",
        "total loss"
    ]

    for severity in severities:

        if severity in text:

            return {
                "field": "incident_severity",
                "operator": "$eq",
                "value": severity,
                "query_type": "text"
            }

    # -----------------------------------------------------
    # VEHICLE MAKE
    # -----------------------------------------------------

    makes = [

        "ford",
        "toyota",
        "honda",
        "chevrolet",
        "dodge",
        "bmw",
        "audi",
        "volkswagen",
        "nissan",
        "subaru",
        "mercedes",
        "jeep",
        "saab",
        "pontiac"
    ]

    for make in makes:

        if make in text:

            return {
                "field": "auto_make",
                "operator": "$eq",
                "value": make,
                "query_type": "text"
            }

    # -----------------------------------------------------
    # CLAIM AMOUNT
    # -----------------------------------------------------

    if "claim" in text:

        number = extract_number(text)

        if number is not None:

            # Greater than
            if (
                "above" in text
                or "over" in text
                or "greater than" in text
                or "more than" in text
                or "higher than" in text
            ):

                return {
                    "field": "total_claim_amount",
                    "operator": "$gt",
                    "value": number,
                    "query_type": "numeric"
                }

            # Less than
            if (
                "below" in text
                or "under" in text
                or "less than" in text
                or "lower than" in text
            ):

                return {
                    "field": "total_claim_amount",
                    "operator": "$lt",
                    "value": number,
                    "query_type": "numeric"
                }

            # Greater than or equal
            if (
                "at least" in text
                or "minimum" in text
                or "or more" in text
            ):

                return {
                    "field": "total_claim_amount",
                    "operator": "$gte",
                    "value": number,
                    "query_type": "numeric"
                }

            # Less than or equal
            if (
                "at most" in text
                or "maximum" in text
                or "or less" in text
            ):

                return {
                    "field": "total_claim_amount",
                    "operator": "$lte",
                    "value": number,
                    "query_type": "numeric"
                }

    # -----------------------------------------------------
    # UNKNOWN SEARCH
    # -----------------------------------------------------

    return None


# =========================================================
# 5. NUMERIC SEARCH
# =========================================================

def numeric_search(
    collection,
    field,
    operator,
    target
):
    """
    Search numeric fields even though MongoDB stores
    their values as strings.

    Values are converted to float in Python before
    comparison.
    """

    results = []

    documents = collection.find(
        {},
        {"_id": 0}
    )

    for document in documents:

        raw_value = document.get(field)

        if raw_value is None:
            continue

        try:

            actual_value = float(raw_value)

        except (
            ValueError,
            TypeError
        ):

            continue

        if (
            operator == "$eq"
            and actual_value == target
        ):

            results.append(document)

        elif (
            operator == "$gt"
            and actual_value > target
        ):

            results.append(document)

        elif (
            operator == "$lt"
            and actual_value < target
        ):

            results.append(document)

        elif (
            operator == "$gte"
            and actual_value >= target
        ):

            results.append(document)

        elif (
            operator == "$lte"
            and actual_value <= target
        ):

            results.append(document)

    return results


# =========================================================
# 6. TEXT SEARCH
# =========================================================

def text_search(
    collection,
    field,
    value
):
    """
    Perform a case-insensitive exact text search.
    """

    query = {

        field: {

            "$regex": (
                "^"
                + re.escape(str(value))
                + "$"
            ),

            "$options": "i"
        }
    }

    return list(
        collection.find(
            query,
            {"_id": 0}
        )
    )


# =========================================================
# 7. EXACT SEARCH
# =========================================================

def exact_search(
    collection,
    field,
    value
):
    """
    Perform an exact search using a string value.
    """

    return list(
        collection.find(
            {
                field: str(value)
            },
            {"_id": 0}
        )
    )


# =========================================================
# 8. EXECUTE SEARCH
# =========================================================

def execute_search(
    collection,
    parsed_query
):
    """
    Execute the generated search.

    Supports:
        numeric
        text
        exact
    """

    if not parsed_query:
        return []

    field = parsed_query.get("field")
    operator = parsed_query.get("operator")
    value = parsed_query.get("value")
    query_type = parsed_query.get("query_type")

    # Safety check
    if not field:
        return []

    if not operator:
        operator = "$eq"

    if query_type == "numeric":

        return numeric_search(
            collection,
            field,
            operator,
            float(value)
        )

    if query_type == "text":

        return text_search(
            collection,
            field,
            value
        )

    return exact_search(
        collection,
        field,
        value
    )


# =========================================================
# 9. DISPLAY RESULTS
# =========================================================

def display_results(results):
    """
    Display matching claim records in a readable format.
    """

    if not results:

        print("\nNo matching claims found.")
        return

    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)

    print(
        "Total matching claims:",
        len(results)
    )

    for index, record in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 60)
        print(f"CLAIM {index}")
        print("-" * 60)

        # Important fields first
        important_fields = [

            "policy_number",
            "age",
            "policy_state",
            "incident_type",
            "incident_severity",
            "incident_state",
            "incident_city",
            "total_claim_amount",
            "fraud_reported"
        ]

        for field in important_fields:

            if field in record:

                print(
                    f"{field}: {record[field]}"
                )

        print("\nFull claim details:")

        for field, value in record.items():

            print(
                f"{field}: {value}"
            )


# =========================================================
# 10. AI SEARCH MENU
# =========================================================

def ai_natural_language_search(collection):
    """
    AI-Assisted / Natural Language Search Menu.
    """

    while True:

        print("\n" + "=" * 60)
        print(
            "AI-ASSISTED NATURAL LANGUAGE SEARCH"
        )
        print("=" * 60)

        print("\n1. Search by Policy Number")
        print("2. Search by Age")
        print("3. Search by Policy State")
        print("4. Search by Incident Type")
        print("5. Search by Incident Severity")
        print("6. Search Fraud Cases")
        print("7. Search by Vehicle Make")
        print("8. Search by Claim Amount")
        print("9. Search by Incident State")
        print("10. Natural Language Search")
        print("0. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        # =================================================
        # 1. POLICY NUMBER
        # =================================================

        if choice == "1":

            policy_number = input(
                "Enter Policy Number: "
            ).strip()

            if not policy_number:

                print(
                    "Policy number cannot be empty."
                )

                continue

            parsed_query = {

                "field": "policy_number",
                "operator": "$eq",
                "value": policy_number,
                "query_type": "exact"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 2. AGE
        # =================================================

        elif choice == "2":

            age = input(
                "Enter Age: "
            ).strip()

            try:

                age_value = float(age)

            except ValueError:

                print(
                    "Please enter a valid age."
                )

                continue

            parsed_query = {

                "field": "age",
                "operator": "$eq",
                "value": age_value,
                "query_type": "numeric"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 3. POLICY STATE
        # =================================================

        elif choice == "3":

            state = input(
                "Enter Policy State "
                "(e.g. OH, IL, IN): "
            ).strip()

            if not state:

                print(
                    "State cannot be empty."
                )

                continue

            parsed_query = {

                "field": "policy_state",
                "operator": "$eq",
                "value": state,
                "query_type": "text"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 4. INCIDENT TYPE
        # =================================================

        elif choice == "4":

            incident_type = input(
                "Enter Incident Type: "
            ).strip()

            if not incident_type:

                print(
                    "Incident type cannot be empty."
                )

                continue

            parsed_query = {

                "field": "incident_type",
                "operator": "$eq",
                "value": incident_type,
                "query_type": "text"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 5. INCIDENT SEVERITY
        # =================================================

        elif choice == "5":

            severity = input(
                "Enter Incident Severity: "
            ).strip()

            if not severity:

                print(
                    "Severity cannot be empty."
                )

                continue

            parsed_query = {

                "field": "incident_severity",
                "operator": "$eq",
                "value": severity,
                "query_type": "text"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 6. FRAUD CASES
        # =================================================

        elif choice == "6":

            parsed_query = {

                "field": "fraud_reported",
                "operator": "$eq",
                "value": "Y",
                "query_type": "exact"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 7. VEHICLE MAKE
        # =================================================

        elif choice == "7":

            make = input(
                "Enter Vehicle Make "
                "(e.g. Ford, Toyota): "
            ).strip()

            if not make:

                print(
                    "Vehicle make cannot be empty."
                )

                continue

            parsed_query = {

                "field": "auto_make",
                "operator": "$eq",
                "value": make,
                "query_type": "text"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 8. CLAIM AMOUNT
        # =================================================

        elif choice == "8":

            amount = input(
                "Enter minimum claim amount: "
            ).strip()

            try:

                amount_value = float(amount)

            except ValueError:

                print(
                    "Please enter a valid amount."
                )

                continue

            parsed_query = {

                "field": "total_claim_amount",
                "operator": "$gte",
                "value": amount_value,
                "query_type": "numeric"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 9. INCIDENT STATE
        # =================================================

        elif choice == "9":

            state = input(
                "Enter Incident State "
                "(e.g. OH, IL, IN): "
            ).strip()

            if not state:

                print(
                    "State cannot be empty."
                )

                continue

            parsed_query = {

                "field": "incident_state",
                "operator": "$eq",
                "value": state,
                "query_type": "text"
            }

            results = execute_search(
                collection,
                parsed_query
            )

            display_results(results)

        # =================================================
        # 10. NATURAL LANGUAGE SEARCH
        # =================================================

        elif choice == "10":

            print("\nExamples:")
            print(
                "• Show claims from Ohio"
            )
            print(
                "• Find customers aged 41"
            )
            print(
                "• Show fraud cases"
            )
            print(
                "• Find Ford vehicles"
            )
            print(
                "• Show claims above 50000"
            )
            print(
                "• Find policy 543610"
            )

            user_input = input(
                "\nEnter your natural language search: "
            ).strip()

            if not user_input:

                print(
                    "Search request cannot be empty."
                )

                continue

            try:

                parsed_query = generate_query(
                    user_input
                )

                if parsed_query is None:

                    print(
                        "\nSorry, I could not "
                        "understand that search."
                    )

                    continue

                print("\nInterpreted Search:")

                print(
                    "Field:",
                    parsed_query["field"]
                )

                print(
                    "Operator:",
                    parsed_query["operator"]
                )

                print(
                    "Value:",
                    parsed_query["value"]
                )

                print(
                    "Query Type:",
                    parsed_query["query_type"]
                )

                results = execute_search(
                    collection,
                    parsed_query
                )

                display_results(results)

            except Exception as error:

                print(
                    "\nAn unexpected error occurred."
                )

                print(
                    "Error:",
                    error
                )

        elif choice == "0":

            print(
                "\nReturning to Main Menu..."
            )

            break

        else:

            print(
                "\nInvalid choice."
            )

            print(
                "Please enter a number "
                "from 0 to 10."
            )


# =========================================================
# 12. PROGRAM START
# =========================================================

if __name__ == "__main__":

    try:

        ai_natural_language_search(
            collection
        )

    except KeyboardInterrupt:

        print(
            "\n\nProgram stopped by user."
        )

    except Exception as error:

        print(
            "\nAn unexpected program error occurred."
        )

        print(
            "Error:",
            error
        )

    finally:

        client.close()

        print(
            "\nMongoDB connection closed."
        )