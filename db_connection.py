from mongodb_connector import MongoDBConnector
uri = "mongodb+srv://aliyasta:2lzTBzOi5d0iplfw@cluster0.ndrzlgu.mongodb.net/?retryWrites=true&w=majority"
db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)
all_data = mongo_connector.get_all_data()

# Вывод данных
for data in all_data:
    print(data)
