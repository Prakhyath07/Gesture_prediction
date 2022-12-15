import pymongo
import os
from gesture_prediction.constants.database import NAMESPACE_NAME
from gesture_prediction.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from dotenv import load_dotenv
load_dotenv()



import pandas as pd
from gesture_prediction.configuration.Cassandra_connection import CassandraSession

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

    
    Cassandra = CassandraSession()
    Cassandra.session.execute("create table gesture_sensor(id int PRIMARY KEY,time int,channel1 float,\
                                channel2 float,channel3 float,channel4 float,\
                                    channel5 float,channel6 float,channel7 float,channel8 float,classes float);")
    
    for ind, i in df.iterrows():
        print(int(i[0]),float(i[1]),float(i[2]),\
            float(i[3]),float(i[4]),float(i[5]),float(i[6]),float(i[7]),float(i[8]),float(i[9]))
        Cassandra.session.execute("insert into gesture_sensor (id,time,channel1,channel2,channel3,\
            channel4,channel5,channel6,channel7,channel8,classes) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[ind,int(i[0]),float(i[1]),float(i[2]),\
            float(i[3]),float(i[4]),float(i[5]),float(i[6]),float(i[7]),float(i[8]),float(i[9])])
        
        

if __name__=="__main__":
    main()