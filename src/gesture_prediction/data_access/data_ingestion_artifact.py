
from gesture_prediction.configuration.mongodb_connection import MongoDBClient
from gesture_prediction.entity.artifact_entity import DataIngestionArtifact
from gesture_prediction.configuration.Cassandra_connection import CassandraSession


class DataIngestionArtifactData:

    def __init__(self):
        self.client = MongoDBClient()
        self.collection_name = "data_ingestion_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_ingestion_artifact(self, data_ingestion_artifact: DataIngestionArtifact):
        self.collection.insert_one(data_ingestion_artifact.to_dict())

    def get_ingestion_artifact(self, query):
        self.collection.find_one(query)

    def update_ingestion_artifact(self, query, data_ingestion_artifact: DataIngestionArtifact):
        self.collection.update_one(query, data_ingestion_artifact.to_dict())

    def remove_ingestion_artifact(self, query):
        self.collection.delete_one(query)

    def remove_ingestion_artifacts(self, query):
        self.collection.delete_many(query)

    def get_ingestion_artifacts(self, query):
        self.collection.find(query)

class DataIngestionArtifactDataCassandra:

    def __init__(self):
        self.cassandra_sess = CassandraSession().session
        self.collection_name = "data_ingestion_artifact"
        

    def save_ingestion_artifact(self, data_ingestion_artifact: DataIngestionArtifact):
        self.cassandra_sess.execute(f"CREATE TABLE IF NOT EXISTS {self.collection_name}tuple([i for i in dir(data_ingestion_artifact) if not i.startswith('_')])")
        self.cassandra_sess.execute(f"select * from {self.collection_name}")