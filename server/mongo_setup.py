import pymongo
from pymongo import MongoClient



def connect_mongo_db_users():
    cluster =MongoClient("mongodb+srv://cyber:521242@orenproject.su4av.mongodb.net/?retryWrites=true&w=majority&appName=OrenProject")
    db = cluster["community_net"]
    collection = db["users"]
    return collection



def add_daemon_to_mongo(data):
    try:
        cluster = MongoClient("mongodb+srv://cyber:521242@orenproject.su4av.mongodb.net/?retryWrites=true&w=majority&appName=OrenProject")
        db = cluster["community_net"]
        collection = db["daemons"]
        collection.insert_one(data)
        print(f"Inserted data with ID: {data}")
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")



