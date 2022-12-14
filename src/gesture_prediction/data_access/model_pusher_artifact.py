from gesture_prediction.configuration.mongodb_connection import MongoDBClient
from gesture_prediction.entity.artifact_entity import ModelPusherArtifact


class ModelPusherArtifactData:

    def __init__(self):
        self.client = MongoDBClient()
        self.collection_name = "model_pusher_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_pusher_artifact(self, model_pusher_artifact: ModelPusherArtifact):
        self.collection.insert_one(model_pusher_artifact.to_dict())

    def get_pusher_artifact(self, query):
        self.collection.find_one(query)

    def update_pusher_artifact(self, query, model_pusher_artifact: ModelPusherArtifact):
        self.collection.update_one(query, model_pusher_artifact.to_dict())

    def remove_pusher_artifact(self, query):
        self.collection.delete_one(query)

    def remove_pusher_artifacts(self, query):
        self.collection.delete_many(query)

    def get_pusher_artifacts(self, query):
        self.collection.find(query)