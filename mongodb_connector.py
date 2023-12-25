from pymongo import MongoClient
from pymongo.server_api import ServerApi


class MongoDBConnector:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.train_data_collection = self.db['train_data']
        
    def insert_or_update_user_data(self, user_data, train_time):
        update = {
            "$push": {"train_times": train_time}
        }
        self.train_data_collection.update_one(user_data, update, upsert=True)

    def get_all_data(self):
        return list(self.train_data_collection.find({}))

    def clear_all_data(self):
        self.train_data_collection.delete_many({})
        
    def update_user_record(self, id, answer_dict):
        query = {"_id": id}
        update = {"$set": answer_dict}
        self.train_data_collection.update_one(query, update)
        
    def get_cancel_data(self, field_name, field_value):
        query = {field_name: field_value}
        return list(self.train_data_collection.find(query))
    
    def get_record_by_id(self, object_id):
        return self.train_data_collection.find_one({"_id": object_id})
    
    def delete_record_by_id(self, object_id):
        self.train_data_collection.delete_one({"_id": object_id})