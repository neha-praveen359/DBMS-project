def update_claim(collection):
    print("\n========== UPDATE CLAIM ==========")

    policy_number = input("Enter Policy Number: ")

    claim = collection.find_one({"policy_number": policy_number})

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

    choice = input("Enter your choice: ")

    if choice == "1":
        value = input("Enter new Policy State: ")
        field = "policy_state"

    elif choice == "2":
        value = input("Enter new Incident Type: ")
        field = "incident_type"

    elif choice == "3":
        value = input("Enter new Incident Severity: ")
        field = "incident_severity"

    elif choice == "4":
        value = float(input("Enter new Total Claim Amount: "))
        field = "total_claim_amount"

    elif choice == "5":
        value = input("Enter new Property Damage (YES/NO): ")
        field = "property_damage"

    elif choice == "6":
        value = input("Enter new Police Report Available (YES/NO): ")
        field = "police_report_available"

    elif choice == "7":
        value = input("Enter new Vehicle Make: ")
        field = "auto_make"

    elif choice == "8":
        value = input("Enter new Vehicle Model: ")
        field = "auto_model"

    else:
        print("Invalid choice.")
        return

    collection.update_one(
        {"policy_number": policy_number},
        {"$set": {field: value}}
    )

    print("Claim updated successfully.")


def delete_claim(collection):
    print("\n========== DELETE CLAIM ==========")

    policy_number = input("Enter Policy Number: ")

    claim = collection.find_one({"policy_number": policy_number})

    if claim is None:
        print("Claim not found.")
        return

    print("\nClaim found.")
    print("Policy Number:", claim.get("policy_number"))
    print("Incident Type:", claim.get("incident_type"))
    print("Claim Amount:", claim.get("total_claim_amount"))

    confirmation = input("\nAre you sure you want to delete this claim? (Y/N): ").upper()

    if confirmation == "Y":
        collection.delete_one({"policy_number": policy_number})
        print("Claim deleted successfully.")

    elif confirmation == "N":
        print("Deletion cancelled.")

    else:
        print("Invalid choice. Deletion cancelled.")