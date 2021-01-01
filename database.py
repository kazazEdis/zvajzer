import os
from pymongo import MongoClient
from settings import load_env

load_env()
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")


cluster = MongoClient(f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.q8z4v.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = cluster['zvajzerDB']
collection = db['operators']

def create(key_vals):
    collection.insert(key_vals)

def read(filter):
    return collection.find_one(filter)

def update(filter, update,):
    collection.update_many(filter, update)

def company(oib):
    collection = db.company
    return collection.find_one({"_id": oib})

def new_company(data):
    collection = db['company']
    collection.insert(data)
