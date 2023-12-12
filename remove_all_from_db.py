from mongodb_connector import MongoDBConnector

uri = "mongodb+srv://aliyasta:2lzTBzOi5d0iplfw@cluster0.ndrzlgu.mongodb.net/?retryWrites=true&w=majority"
db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)

mongo_connector.clear_all_data()
print("Все данные были удалены.")