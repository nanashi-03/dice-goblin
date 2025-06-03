import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")
db_name = "pf2e"

client = MongoClient(mongo_uri)
db = client[db_name]
characters = db.characters  # Now stores one character per user