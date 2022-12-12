from gesture_prediction.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig
from gesture_prediction.entity.artifact_entity import DataIngestionArtifact
from gesture_prediction.exception import GestureException
import sys,os
from gesture_prediction.logger import logging
from gesture_prediction.components.data_ingestion import DataIngestion
from gesture_prediction.constants.training_pipeline import SAVED_MODEL_DIR


class TrainPipeline:
    is_pipeline_running = False
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        # self.s3_sync = S3Sync()
        


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


    def run_pipeline(self):
        try:
            TrainPipeline.is_pipeline_running = True
            logging.info("Starting training pipeline")
            data_ingestion_artifact:DataIngestionArtifact = self.start_data_ingestion()
            logging.info("Training pipeline completed")
            
        except  Exception as e:
            # self.sync_artifact_dir_to_s3()
            TrainPipeline.is_pipeline_running = False
            raise  GestureException(e,sys)
