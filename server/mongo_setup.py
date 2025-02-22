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



def add_file(peer_id,file_hash,file_name):
    try:
        cluster = MongoClient("mongodb+srv://cyber:521242@orenproject.su4av.mongodb.net/?retryWrites=true&w=majority&appName=OrenProject")
        db = cluster["community_net"]
        collection = db["files"]
        file_info={"peer-id":peer_id,"file-hash":file_hash,"file-name":file_name}
        collection.insert_one(file_info)
        print(f"Inserted data with ID: {file_info}")
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")


def get_files_available():
    cluster = MongoClient("mongodb+srv://cyber:521242@orenproject.su4av.mongodb.net/?retryWrites=true&w=majority&appName=OrenProject")
    db = cluster["community_net"]
    collection = db["files"]
    file_data = collection.find({}, {"file-name": 1, "file-hash": 1, "_id": 0})
    file_list = [(doc["file-name"], doc["file-hash"]) for doc in file_data]
    return file_list
