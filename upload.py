import os
import csv
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Connect to MongoDB Atlas safely using your .env file
load_dotenv()
mongo_url = os.getenv("MONGODB_URI")
client = MongoClient(mongo_url)

# 2. Target your database and your exact collection name
db = client["insurance_company"]
records_collection = db["insurance_data"]  # Updated to match your name!

# 3. Target your CSV file
csv_filename = "dataset.csv"

print("⏳ Opening your file and preparing your data...")

try:
    # Read your CSV rows and convert them into a format MongoDB understands
    with open(csv_filename, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        data_to_insert = [row for row in csv_reader]
        
    if data_to_insert:
        print(f"🚀 Found {len(data_to_insert)} rows! Uploading them to the cloud...")
        
        # This sends all your rows up to the cloud at the same time
        result = records_collection.insert_many(data_to_insert)
        print(f"✨ SUCCESS! Uploaded {len(result.inserted_ids)} records to MongoDB!")
    else:
        print("⚠️ Warning: Your dataset.csv file appears to be completely empty.")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{csv_filename}' in this folder. Make sure it is next to app.py!")
except Exception as e:
    print(f"❌ Upload failed: {e}")