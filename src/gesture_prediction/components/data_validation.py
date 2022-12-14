from gesture_prediction.constants.training_pipeline import SCHEMA_FILE_PATH
from gesture_prediction.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from gesture_prediction.entity.config_entity import DataValidationConfig
from gesture_prediction.exception import GestureException
from gesture_prediction.logger import logging
from gesture_prediction.utils.main_utils import read_yaml_file,write_yaml_file
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
from typing import List
from gesture_prediction.data_access.data_validation_artifact import DataValidationArtifactData

class DataValidation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                        data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self.data_validation_artifact_data = DataValidationArtifactData()
        except Exception as e:
            raise  GestureException(e,sys)
    
    def drop_zero_std_columns(self,dataframe:pd.DataFrame) -> List:
        logging.info("checking for columns with zero standard deviation")
        cols = dataframe.columns
        zero_std=[]
        for col in cols[:]:
            if (dataframe[[col]].describe().loc['std',:]).get(col) ==0:
                zero_std.append(col)
                logging.info(f"column {col} has zero std deviation")
        return zero_std


    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            logging.info("validation of number of columns started")
            number_of_columns = len(self._schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns:
                return True
            return False
        except Exception as e:
            raise GestureException(e,sys)

    def is_numerical_column_exist(self,dataframe:pd.DataFrame)->bool:
        try:
            logging.info("validation of number of numerical columns started")
            numerical_columns = self._schema_config["numerical_columns"]
            dataframe_columns = dataframe.columns

            numerical_column_present = True
            missing_numerical_columns = []
            for num_column in numerical_columns:
                if num_column not in dataframe_columns:
                    numerical_column_present=False
                    missing_numerical_columns.append(num_column)
            
            logging.info(f"Missing numerical columns: [{missing_numerical_columns}]")
            return numerical_column_present
        except Exception as e:
            raise GestureException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise GestureException(e,sys)
    

    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            logging.info("checking for data drift")
            status=True
            report ={}
            for column in base_df.columns:
                d1 = base_df[column]
                d2  = current_df[column]
                is_same_dist = ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found = True 
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
            
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            
            #Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report,)
            logging.info(f"Distribution is same: {status}")
            return status
        except Exception as e:
            raise GestureException(e,sys)
   

    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            error_message = ""
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            #Reading data from train and test file location
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            #Validate number of columns
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"{error_message}Train dataframe does not contain all columns.\n"
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"{error_message}Test dataframe does not contain all columns.\n"
        

            #Validate numerical columns

            status = self.is_numerical_column_exist(dataframe=train_dataframe)
            if not status:
                error_message=f"{error_message}Train dataframe does not contain all numerical columns.\n"
            
            status = self.is_numerical_column_exist(dataframe=test_dataframe)
            if not status:
                error_message=f"{error_message}Test dataframe does not contain all numerical columns.\n"
            
            if len(error_message)>0:
                raise Exception(error_message)

            #Let check data drift
            status = self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )

            logging.info("saving data validation artifact to database")
            self.data_validation_artifact_data.save_validation_artifact(data_validation_artifact=data_validation_artifact)
            return data_validation_artifact
        except Exception as e:
            raise GestureException(e,sys)