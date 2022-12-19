import pymongo
from gesture_prediction.constants.database import DATABASE_NAME
from gesture_prediction.constants.environment.variable_key import MONGO_DB_URL_ENV_KEY
import certifi
import os


ca = certifi.where()


class MongoDBClient:
    client = None
    def __init__(self, database_name=DATABASE_NAME) -> None:
        try:
            if MongoDBClient.client is None:
                mongo_db_url = os.getenv(MONGO_DB_URL_ENV_KEY)
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
        except Exception as e:
            raise e