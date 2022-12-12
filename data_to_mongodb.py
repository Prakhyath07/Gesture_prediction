import pymongo
import os
from gesture_prediction.constants.database import DATABASE_NAME
from gesture_prediction.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from gesture_prediction.constants.environment.variable_key import MONGO_DB_URL_ENV_KEY
from dotenv import load_dotenv
load_dotenv()

import certifi
ca = certifi.where()

import pandas as pd
class MongodbOperation:

    def __init__(self) -> None:

        self.client = pymongo.MongoClient(os.getenv('MONGO_DB_URL'),tlsCAFile=ca)
        self.db_name=DATABASE_NAME

    def insert_many(self,collection_name,records:list):
        self.client[self.db_name][collection_name].insert_many(records)

    def insert(self,collection_name,record):
        self.client[self.db_name][collection_name].insert_one(record)

data_path = r"C:\ineuron\Industry_ready_projects\Gesture_prediction\EMG_data_for_gestures-master (1)\EMG_data_for_gestures-master"

def main():
    df = pd.DataFrame()
    for i in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path,i)):
            for j in os.listdir(os.path.join(data_path,i)):
                temp = pd.read_csv(os.path.join(data_path,i,j),sep="\t")
                index = temp[temp['class']!=0].index
                temp=temp.iloc[index]
                df=pd.concat([df,temp],axis=0)

    
    mongodb = MongodbOperation()
    
    records = df.to_dict('records')
    print("records")
    mongodb.insert_many(collection_name=DATA_INGESTION_COLLECTION_NAME, records=records)

if __name__=="__main__":
    main()