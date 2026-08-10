# ============================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================

def get_required_input(message):
    while True:
        value = input(message).strip()

        if value == "":
            print("This field cannot be empty.")
        else:
            return value


def get_integer(message):
    while True:
        try:
            value = int(input(message))
            return value

        except ValueError:
            print("Please enter a valid integer.")


def get_positive_integer(message):
    while True:
        try:
            value = int(input(message))

            if value < 0:
                print("Value cannot be negative.")
            else:
                return value

        except ValueError:
            print("Please enter a valid integer.")


def get_float(message):
    while True:
        try:
            value = float(input(message))
            return value

        except ValueError:
            print("Please enter a valid number.")


def get_positive_float(message):
    while True:
        try:
            value = float(input(message))

            if value < 0:
                print("Value cannot be negative.")
            else:
                return value

        except ValueError:
            print("Please enter a valid number.")


def get_incident_hour():
    while True:
        try:
            hour = int(input("Incident Hour (0-23): "))

            if 0 <= hour <= 23:
                return hour

            print("Incident hour must be between 0 and 23.")

        except ValueError:
            print("Please enter a valid hour.")


# ============================================================
# FILTER CLAIMS
# ============================================================

def filter_claims(collection):

    print("\n===================================")
    print("          FILTER CLAIMS")
    print("===================================")

    print("1. Claim Amount Range")
    print("2. Age Range")
    print("3. Incident State + Incident Type")
    print("4. Vehicle Make + Claim Amount")

    choice = input("Enter your choice: ").strip()

    query = {}

    # --------------------------------------------------------
    # 1. CLAIM AMOUNT RANGE
    # --------------------------------------------------------

    if choice == "1":

        min_amount = get_positive_float(
            "Enter minimum claim amount: "
        )

        max_amount = get_positive_float(
            "Enter maximum claim amount: "
        )

        if min_amount > max_amount:
            print("Minimum amount cannot be greater than maximum amount.")
            return

        query["total_claim_amount"] = {
            "$gte": min_amount,
            "$lte": max_amount
        }

    # --------------------------------------------------------
    # 2. AGE RANGE
    # --------------------------------------------------------

    elif choice == "2":

        min_age = get_positive_integer(
            "Enter minimum age: "
        )

        max_age = get_positive_integer(
            "Enter maximum age: "
        )

        if min_age > max_age:
            print("Minimum age cannot be greater than maximum age.")
            return

        query["age"] = {
            "$gte": min_age,
            "$lte": max_age
        }

    # --------------------------------------------------------
    # 3. INCIDENT STATE + INCIDENT TYPE
    # --------------------------------------------------------

    elif choice == "3":

        state = get_required_input(
            "Enter Incident State: "
        )

        incident_type = get_required_input(
            "Enter Incident Type: "
        )

        query["incident_state"] = state
        query["incident_type"] = incident_type

    # --------------------------------------------------------
    # 4. VEHICLE MAKE + CLAIM AMOUNT
    # --------------------------------------------------------

    elif choice == "4":

        vehicle_make = get_required_input(
            "Enter Vehicle Make: "
        )

        amount = get_positive_float(
            "Enter minimum claim amount: "
        )

        query["auto_make"] = vehicle_make

        query["total_claim_amount"] = {
            "$gte": amount
        }

    # --------------------------------------------------------
    # INVALID MENU OPTION
    # --------------------------------------------------------

    else:
        print("Invalid choice.")
        return

    # ========================================================
    # SEARCH DATABASE
    # ========================================================

    results = collection.find(query)

    count = 0

    print("\n===================================")
    print("          FILTER RESULTS")
    print("===================================")

    for claim in results:

        count += 1

        print("\n-----------------------------------")
        print("Policy Number:",
              claim.get("policy_number"))

        print("Age:",
              claim.get("age"))

        print("Incident State:",
              claim.get("incident_state"))

        print("Incident Type:",
              claim.get("incident_type"))

        print("Vehicle:",
              claim.get("auto_make"),
              claim.get("auto_model"))

        print("Claim Amount:",
              claim.get("total_claim_amount"))

    if count == 0:
        print("\nNo matching claims found.")

    else:
        print("\nTotal matching claims:", count)
```
