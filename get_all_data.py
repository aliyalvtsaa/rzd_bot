from mongodb_connector import MongoDBConnector
from config import uri

db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)
all_data = mongo_connector.get_all_data()

for data in all_data:
    print(data)
    
