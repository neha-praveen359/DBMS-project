def create_claim(collection):
    print("\n========== REGISTER NEW CLAIM ==========")

    # ---------------- POLICY ----------------
    print("\n--- POLICY DETAILS ---")

    months_as_customer = int(input("Months as Customer: "))
    age = int(input("Age: "))
    policy_number = input("Policy Number: ")
    policy_bind_date = input("Policy Bind Date (YYYY-MM-DD): ")
    policy_state = input("Policy State: ")
    policy_csl = input("Policy CSL: ")
    policy_deductable = float(input("Policy Deductable: "))
    policy_annual_premium = float(input("Policy Annual Premium: "))
    umbrella_limit = int(input("Umbrella Limit: "))
    insured_zip = int(input("Insured ZIP: "))

    # ---------------- INSURED ----------------
    print("\n--- INSURED DETAILS ---")

    insured_sex = input("Insured Sex: ")
    insured_education_level = input("Insured Education Level: ")
    insured_occupation = input("Insured Occupation: ")
    insured_hobbies = input("Insured Hobbies: ")
    insured_relationship = input("Insured Relationship: ")
    capital_gains = int(input("Capital Gains: "))
    capital_loss = int(input("Capital Loss: "))

    # ---------------- INCIDENT ----------------
    print("\n--- INCIDENT DETAILS ---")

    incident_date = input("Incident Date (YYYY-MM-DD): ")
    incident_type = input("Incident Type: ")
    collision_type = input("Collision Type: ")
    incident_severity = input("Incident Severity: ")
    authorities_contacted = input("Authorities Contacted: ")
    incident_state = input("Incident State: ")
    incident_city = input("Incident City: ")
    incident_location = input("Incident Location: ")
    incident_hour_of_the_day = int(input("Incident Hour (0-23): "))
    number_of_vehicles_involved = int(input("Number of Vehicles Involved: "))

    # ---------------- DAMAGE / EVIDENCE ----------------
    print("\n--- DAMAGE / EVIDENCE DETAILS ---")

    property_damage = input("Property Damage (YES/NO): ")
    bodily_injuries = int(input("Bodily Injuries: "))
    witnesses = int(input("Witnesses: "))
    police_report_available = input("Police Report Available (YES/NO): ")

    # ---------------- CLAIM ----------------
    print("\n--- CLAIM DETAILS ---")

    total_claim_amount = float(input("Total Claim Amount: "))
    injury_claim = float(input("Injury Claim: "))
    property_claim = float(input("Property Claim: "))
    vehicle_claim = float(input("Vehicle Claim: "))

    # ---------------- VEHICLE ----------------
    print("\n--- VEHICLE DETAILS ---")

    auto_make = input("Auto Make: ")
    auto_model = input("Auto Model: ")
    auto_year = int(input("Auto Year: "))

    # ---------------- HISTORICAL LABEL ----------------
    print("\n--- HISTORICAL LABEL ---")

    fraud_reported = input("Fraud Reported (Y/N): ")

    # ---------------- CREATE DOCUMENT ----------------

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

    # ---------------- INSERT ----------------

    collection.insert_one(claim)

    print("\nClaim registered successfully!")