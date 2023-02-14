from gesture_prediction.entity.config_entity import (TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,
DataTransformationConfig,ModelTrainerConfig,ModelEvaluationConfig,ModelPusherConfig)
from gesture_prediction.entity.artifact_entity import (DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,
ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact)
from gesture_prediction.exception import GestureException
import sys,os
from gesture_prediction.logger import logging
from gesture_prediction.components.data_ingestion import DataIngestion
from gesture_prediction.components.data_validation import DataValidation
from gesture_prediction.components.data_transformation import DataTransformation
from gesture_prediction.components.model_trainer import ModelTrainer
from gesture_prediction.components.model_evaluation import ModelEvaluation
from gesture_prediction.components.model_pusher import ModelPusher
from gesture_prediction.constants.training_pipeline import SAVED_MODEL_DIR
from gesture_prediction.cloud_storage.s3_syncer import S3Sync
from gesture_prediction.constants.s3_bucket import TRAINING_BUCKET_NAME


class TrainPipeline:
    is_pipeline_running = False
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()
        


    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except  Exception as e:
            raise  GestureException(e,sys)
    
    def start_data_validaton(self,data_ingestion_artifact:DataIngestionArtifact)->DataValidationArtifact:
        try:
            logging.info("Starting data validation")
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config = data_validation_config
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f"Data validation completed and artifact: {data_validation_artifact}")
            return data_validation_artifact
        except  Exception as e:
            raise  GestureException(e,sys)

    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact) ->DataTransformationArtifact:
        try:
            logging.info("Starting data transformation")
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config
            )
            data_transformation_artifact =  data_transformation.initiate_data_transformation()
            logging.info(f"Data transformation completed and artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except  Exception as e:
            raise  GestureException(e,sys)
    
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact) ->ModelTrainerArtifact:
        try:
            logging.info("Starting Model trainer")
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info(f"Model Training completed and artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except  Exception as e:
            raise  GestureException(e,sys)

    def start_model_evaluation(self,data_validation_artifact: DataValidationArtifact, 
                                model_trainer_artifact: ModelTrainerArtifact) ->ModelEvaluationArtifact:
        try:
            logging.info("model evaluation started")
            model_evaluation_config = ModelEvaluationConfig(training_pipeline_config=self.training_pipeline_config)
            model_eval = ModelEvaluation(model_eval_config=model_evaluation_config,
                                         model_trainer_artifact=model_trainer_artifact,
                                         data_validation_artifact=data_validation_artifact
                                        )
            model_eval_artifact = model_eval.initiate_model_evaluation()
            logging.info(f"Model evaluation completed and artifact: {model_eval_artifact}")
            return model_eval_artifact
        except  Exception as e:
            raise  GestureException(e,sys)
    
    def start_model_pusher(self, model_eval_artifact: ModelEvaluationArtifact) ->ModelPusherArtifact:
        try:
            logging.info("model pusher stage started")
            model_pusher_config = ModelPusherConfig(training_pipeline_config=self.training_pipeline_config)
            model_pusher = ModelPusher(model_pusher_config=model_pusher_config,
                                    model_eval_artifact=model_eval_artifact
                                    )
            model_pusher_artifact = model_pusher.initiate_model_pusher()
            logging.info(f"Model pusher stage completed and artifact: {model_pusher_artifact}")
            return model_pusher_artifact

        except  Exception as e:
            raise  GestureException(e,sys)
    
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise GestureException(e,sys)
            
    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/{SAVED_MODEL_DIR}"
            self.s3_sync.sync_folder_to_s3(folder = SAVED_MODEL_DIR,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise GestureException(e,sys)

    def run_pipeline(self):
        try:
            TrainPipeline.is_pipeline_running = True
            logging.info("Starting training pipeline")
            data_ingestion_artifact:DataIngestionArtifact = self.start_data_ingestion()
            data_validation_artifact=self.start_data_validaton(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            model_eval_artifact = self.start_model_evaluation(data_validation_artifact=data_validation_artifact,model_trainer_artifact=model_trainer_artifact)
            if not model_eval_artifact.is_model_accepted:
                print("training completed but new model is not accepted")
                logging.info("Trained model is not better than the best model")
                raise Exception("Trained model is not better than the best model")
            
            model_pusher_artifact = self.start_model_pusher(model_eval_artifact=model_eval_artifact)
            TrainPipeline.is_pipeline_running = False
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
            logging.info("Training pipeline completed")
            
        except  Exception as e:
            self.sync_artifact_dir_to_s3()
            TrainPipeline.is_pipeline_running = False
            raise  GestureException(e,sys)
