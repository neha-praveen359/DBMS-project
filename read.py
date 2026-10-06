def search_claims(collection):
    print("\n===== SEARCH CLAIMS =====")
    print("1. Search by Policy Number")
    print("2. Search by Age")
    print("3. Search by Policy State")
    print("4. Search by Fraud Status")
    print("5. Search by Claim Amount Range")

    choice = input("Enter your choice: ")

    query = {}

    if choice == "1":
        policy_number = input("Enter Policy Number: ")
        query = {"policy_number": policy_number}

    elif choice == "2":
        age = input("Enter Age: ")
        query = {"age": int(age)}

    elif choice == "3":
        policy_state = input("Enter Policy State: ")
        query = {
            "policy_state": {
                "$regex": policy_state,
                "$options": "i"
            }
        }

    elif choice == "4":
        fraud_status = input("Enter Fraud Status (Y/N): ")
        query = {
            "fraud_reported": {
                "$regex": fraud_status,
                "$options": "i"
            }
        }

    elif choice == "5":
        minimum = input("Enter minimum claim amount: ")
        maximum = input("Enter maximum claim amount: ")

        query = {
            "total_claim_amount": {
                "$gte": float(minimum),
                "$lte": float(maximum)
            }
        }

    else:
        print("Invalid choice.")
        return

    results = collection.find(query)

    found = False

    print("\n===== SEARCH RESULTS =====")

    for claim in results:
        found = True

        print("--------------------------------")
        print("Policy Number  :", claim.get("policy_number"))
        print("Age            :", claim.get("age"))
        print("Policy State   :", claim.get("policy_state"))
        print("Claim Amount   :", claim.get("total_claim_amount"))
        print("Fraud Reported :", claim.get("fraud_reported"))

    if not found:
        print("No claims found.")