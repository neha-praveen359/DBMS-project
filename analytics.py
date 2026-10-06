from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(override=True)

mongo_url = os.getenv("MONGODB_URI")

client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)

client.admin.command("ping")
print("MongoDB Atlas connection successful!\n")

db = client["insurance_company"]
collection = db["insurance_data"]

# 1. Claims by Incident Type
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


# 2. Claims by Incident State
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


# 3. Fraud vs Non-Fraud
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


# 4. Average Claim Amount by Fraud Status
def average_claim_by_fraud_status(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$fraud_reported",
                "average_claim_amount": {
                    "$avg": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            }
        },
        {
            "$sort": {"average_claim_amount": -1}
        }
    ]

    return list(collection.aggregate(pipeline))


# 5. Claims by Vehicle Make
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
# 6. Average Claim Amount by Incident Type
def average_claim_by_incident_type(collection):
    pipeline = [
        {
            "$group": {
                "_id": "$incident_type",
                "average_claim_amount": {
                    "$avg": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            }
        },
        {
            "$sort": {"average_claim_amount": -1}
        }
    ]

    return list(collection.aggregate(pipeline))
print("\n--- Claims by Incident Type ---")
for result in claims_by_incident_type(collection):
    print(result)

print("\n--- Claims by Incident State ---")
for result in claims_by_incident_state(collection):
    print(result)

print("\n--- Fraud vs Non-Fraud ---")
for result in fraud_vs_nonfraud(collection):
    print(result)

print("\n--- Average Claim Amount by Fraud Status ---")
for result in average_claim_by_fraud_status(collection):
    print(result)

print("\n--- Claims by Vehicle Make ---")
for result in claims_by_vehicle_make(collection):
    print(result)
print("\n--- Average Claim Amount by Incident Type ---")
for result in average_claim_by_incident_type(collection):
    print(result)