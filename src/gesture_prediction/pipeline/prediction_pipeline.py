from gesture_prediction.entity.config_entity import PredictionPipelineConfig
from gesture_prediction.entity.artifact_entity import PredictionArtifact
from gesture_prediction.exception import GestureException
import sys,os
from gesture_prediction.logger import logging


from io import BytesIO
import pandas as pd
from gesture_prediction.constants.training_pipeline import SCHEMA_FILE_PATH
from gesture_prediction.utils.main_utils import read_yaml_file
from gesture_prediction.constants.training_pipeline import SAVED_MODEL_DIR
from gesture_prediction.ml.model.estimator import ModelResolver,TargetValueMapping
from gesture_prediction.utils.main_utils import load_object


class PredictPipeline:
    def __init__(self,input_data):
        self.prediction_pipeline_config = PredictionPipelineConfig()
        self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        self.input_data = input_data
        # self.s3_sync = S3Sync()
        


    def read_data_from_api(self)-> pd.DataFrame:
        try:
            
            logging.info("Reading data")
            
            df= pd.read_csv(BytesIO(self.input_data))
            df = df.drop(self.schema_config["drop_columns"],axis=1)
            return df
        except  Exception as e:
            raise  GestureException(e,sys)

    def save_to_csv(self,data:pd.DataFrame, path):
        try:
            
            logging.info(f"saving data to csv in {path}")
            
            data.to_csv(path)
            
        except  Exception as e:
            raise  GestureException(e,sys)

    def predict(self,data:pd.DataFrame) -> pd.DataFrame:
        model_resolver = ModelResolver(model_dir=SAVED_MODEL_DIR)
        if not model_resolver.is_model_exists():
            raise Exception("Model is not available")
        
        best_model_path = model_resolver.get_best_model_path()
        model = load_object(file_path=best_model_path)
        y_pred = model.predict(data)
        pred_df = pd.DataFrame(y_pred,columns=["predicted_column"])
        pred_df['predicted_column'].replace(TargetValueMapping().reverse_mapping(),inplace=True)

        return pred_df

    
            


    def run_pipeline(self):
        try:
            logging.info("reading data from input file")
            input_df =self.read_data_from_api()
            artifact_dir = self.prediction_pipeline_config.artifact_dir
            os.makedirs(artifact_dir,exist_ok=True)
            self.save_to_csv(input_df,self.prediction_pipeline_config.input_file_path)

            pred_df = self.predict(input_df)
            self.save_to_csv(pred_df,self.prediction_pipeline_config.pred_file_path)

            pred_artifact = PredictionArtifact(
                input_file_path= self.prediction_pipeline_config.input_file_path,
                prediction_file_path= self.prediction_pipeline_config.pred_file_path

            )
            
            # self.sync_artifact_dir_to_s3()
            
            

            return pred_artifact

        except  Exception as e:
            # self.sync_artifact_dir_to_s3()
            raise  GestureException(e,sys)