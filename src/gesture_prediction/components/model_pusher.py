
from gesture_prediction.exception import GestureException
from gesture_prediction.logger import logging
from gesture_prediction.entity.artifact_entity import ModelPusherArtifact,ModelTrainerArtifact,ModelEvaluationArtifact
from gesture_prediction.entity.config_entity import ModelEvaluationConfig,ModelPusherConfig
import os,sys
from gesture_prediction.ml.metric.classification_metric import get_classification_score
from gesture_prediction.utils.main_utils import save_object,load_object,write_yaml_file
from gesture_prediction.data_access.model_pusher_artifact import ModelPusherArtifactData
import shutil

class ModelPusher:

    def __init__(self,
                model_pusher_config:ModelPusherConfig,
                model_eval_artifact:ModelEvaluationArtifact):

        try:
            self.model_pusher_config = model_pusher_config
            self.model_eval_artifact = model_eval_artifact
            self.model_pusher_artifact_data = ModelPusherArtifactData()
        except  Exception as e:
            raise GestureException(e, sys)
    

    def initiate_model_pusher(self,)->ModelPusherArtifact:
        try:
            trained_model_path = self.model_eval_artifact.trained_model_path
            
            #Creating model pusher dir to save model
            logging.info("Creating model pusher dir to save model")
            model_file_path = self.model_pusher_config.model_file_path
            os.makedirs(os.path.dirname(model_file_path),exist_ok=True)
            shutil.copy(src=trained_model_path, dst=model_file_path)

            #saved model dir
            logging.info("Creating saved model dir to save best model")
            saved_model_path = self.model_pusher_config.saved_model_path
            os.makedirs(os.path.dirname(saved_model_path),exist_ok=True)
            shutil.copy(src=trained_model_path, dst=saved_model_path)

            #prepare artifact
            model_pusher_artifact = ModelPusherArtifact(saved_model_path=saved_model_path, model_file_path=model_file_path)
            logging.info("saving model pusher artifact to database")
            self.model_pusher_artifact_data.save_pusher_artifact(model_pusher_artifact=model_pusher_artifact)
            return model_pusher_artifact
        except  Exception as e:
            raise GestureException(e, sys)
    