import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
