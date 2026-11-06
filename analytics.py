from pymongo.errors import PyMongoError


# ============================================================
# 1. CLAIMS BY INCIDENT TYPE
# ============================================================

def claims_by_incident_type(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$incident_type",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 2. CLAIMS BY INCIDENT STATE
# ============================================================

def claims_by_incident_state(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$incident_state",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 3. FRAUD VS NON-FRAUD
# ============================================================

def fraud_vs_nonfraud(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$fraud_reported",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 4. CLAIMS BY VEHICLE MAKE
# ============================================================

def claims_by_vehicle_make(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$auto_make",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 5. CLAIMS BY VEHICLE MODEL
# ============================================================

def claims_by_vehicle_model(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$auto_model",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 6. CLAIMS BY VEHICLE YEAR
# ============================================================

def claims_by_vehicle_year(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$auto_year",
                "claim_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"claim_count": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# ============================================================
# 7. INCIDENT, FRAUD & VEHICLE ANALYSIS
# ============================================================

def display_analysis(title, results):
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

    if not results:
        print("No data found.")
        return

    for result in results:
        print(
            f"{str(result.get('_id')):<30} : "
            f"{result.get('claim_count')}"
        )


def incident_fraud_vehicle_analysis(collection):

    print("\n" + "=" * 60)
    print("        INCIDENT, FRAUD & VEHICLE ANALYSIS")
    print("=" * 60)

    try:
        display_analysis(
            "CLAIMS BY INCIDENT TYPE",
            claims_by_incident_type(collection)
        )

        display_analysis(
            "CLAIMS BY INCIDENT STATE",
            claims_by_incident_state(collection)
        )

        display_analysis(
            "FRAUD VS NON-FRAUD",
            fraud_vs_nonfraud(collection)
        )

        display_analysis(
            "CLAIMS BY VEHICLE MAKE",
            claims_by_vehicle_make(collection)
        )

        display_analysis(
            "CLAIMS BY VEHICLE MODEL",
            claims_by_vehicle_model(collection)
        )

        display_analysis(
            "CLAIMS BY VEHICLE YEAR",
            claims_by_vehicle_year(collection)
        )

        print("\n" + "=" * 60)

    except PyMongoError as error:
        print("\nUnable to perform analysis.")
        print("Error:", error)


# ============================================================
# 8. MENU
# ============================================================

def incident_fraud_vehicle_menu(collection):

    while True:
        print("\n" + "=" * 60)
        print("        INCIDENT, FRAUD & VEHICLE ANALYSIS")
        print("=" * 60)

        print("1. Claims by Incident Type")
        print("2. Claims by Incident State")
        print("3. Fraud vs Non-Fraud")
        print("4. Claims by Vehicle Make")
        print("5. Claims by Vehicle Model")
        print("6. Claims by Vehicle Year")
        print("7. Display All Analysis")
        print("0. Back to Main Menu")

        print("=" * 60)

        choice = input("Enter your choice (0-7): ").strip()

        try:
            if choice == "1":
                display_analysis(
                    "CLAIMS BY INCIDENT TYPE",
                    claims_by_incident_type(collection)
                )

            elif choice == "2":
                display_analysis(
                    "CLAIMS BY INCIDENT STATE",
                    claims_by_incident_state(collection)
                )

            elif choice == "3":
                display_analysis(
                    "FRAUD VS NON-FRAUD",
                    fraud_vs_nonfraud(collection)
                )

            elif choice == "4":
                display_analysis(
                    "CLAIMS BY VEHICLE MAKE",
                    claims_by_vehicle_make(collection)
                )

            elif choice == "5":
                display_analysis(
                    "CLAIMS BY VEHICLE MODEL",
                    claims_by_vehicle_model(collection)
                )

            elif choice == "6":
                display_analysis(
                    "CLAIMS BY VEHICLE YEAR",
                    claims_by_vehicle_year(collection)
                )

            elif choice == "7":
                incident_fraud_vehicle_analysis(collection)

            elif choice == "0":
                break

            else:
                print("\nInvalid choice. Enter a number from 0 to 7.")

        except PyMongoError as error:
            print("\nUnable to run the selected analysis.")
            print("Error:", error)
