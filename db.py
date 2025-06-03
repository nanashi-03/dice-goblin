import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
db_name = "pf2e"

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # will raise an exception if cannot connect
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

db = client[db_name]
characters = db.characters  # Now stores one character per user