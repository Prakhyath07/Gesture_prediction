from gesture_prediction.configuration.mongodb_connection import MongoDBClient
from gesture_prediction.entity.artifact_entity import ModelTrainerArtifact


class ModelTrainerArtifactData:

    def __init__(self):
        self.client = MongoDBClient()
        self.collection_name = "model_trainer_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_trainer_artifact(self, model_trainer_artifact: ModelTrainerArtifact):
        self.collection.insert_one(model_trainer_artifact._asdict())

    def get_trainer_artifact(self, query):
        self.collection.find_one(query)

    def update_trainer_artifact(self, query, model_trainer_artifact: ModelTrainerArtifact):
        self.collection.update_one(query, model_trainer_artifact._asdict())

    def remove_trainer_artifact(self, query):
        self.collection.delete_one(query)

    def remove_trainer_artifacts(self, query):
        self.collection.delete_many(query)

    def get_trainer_artifacts(self, query):
        self.collection.find(query)