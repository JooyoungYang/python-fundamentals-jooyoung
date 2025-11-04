from pymongo import MongoClient

client = MongoClient("mongodb://admin:adminpassword@localhost:27017/")
db = client["dataeng"]

print(db.list_collection_names())
for doc in db["users"].find():
    print(doc)
