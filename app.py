import os
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Load environment variables from your secure .env file
load_dotenv()

# 2. Establish the connection to your live MongoDB Atlas cloud database
mongo_url = os.getenv("MONGODB_URI")
client = MongoClient(mongo_url)

# 3. Define your target database and collections
# Feel free to change "group_project_db" to whatever you want to name your project database
db = client["group_project_db"]
users_collection = db["users"] 

print("🚀 Connected to MongoDB! Your project backend is fully active.")