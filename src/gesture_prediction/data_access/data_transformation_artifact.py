from gesture_prediction.configuration.mongodb_connection import MongoDBClient
from gesture_prediction.entity.artifact_entity import DataTransformationArtifact


class DataTransformationArtifactData:

    def __init__(self):
        self.client = MongoDBClient()
        self.collection_name = "data_transformation_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_transformation_artifact(self, data_transformation_artifact: DataTransformationArtifact):
        self.collection.insert_one(data_transformation_artifact.to_dict())

    def get_transformation_artifact(self, query):
        self.collection.find_one(query)

    def update_transformation_artifact(self, query, data_transformation_artifact: DataTransformationArtifact):
        self.collection.update_one(query, data_transformation_artifact.to_dict())

    def remove_transformation_artifact(self, query):
        self.collection.delete_one(query)

    def remove_transformation_artifacts(self, query):
        self.collection.delete_many(query)

    def get_transformation_artifacts(self, query):
        self.collection.find(query)