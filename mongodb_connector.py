from pymongo import MongoClient
from pymongo.server_api import ServerApi

class MongoDBConnector:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.train_data_collection = self.db['train_data']

    def insert_initial_data(self, chat_id, user_needs):
        self.train_data_collection.insert_one({"chat_id": chat_id, "user_needs": user_needs})

    def update_train_time(self, chat_id, train_time):
        self.train_data_collection.update_one({"chat_id": chat_id}, {"$push": {"train_times": train_time}})
        
    def get_all_data(self):
        return list(self.train_data_collection.find({}))

    def clear_all_data(self):
        self.train_data_collection.delete_many({})