from gesture_prediction.exception import GestureException
from gesture_prediction.logger import logging
from gesture_prediction.entity.config_entity import DataIngestionConfig
from gesture_prediction.entity.artifact_entity import DataIngestionArtifact
from sklearn.model_selection import train_test_split
import os,sys
from pandas import DataFrame
from gesture_prediction.data_access.sensor_data import GestureData,GestureDataCassandra
from gesture_prediction.utils.main_utils import read_yaml_file
from gesture_prediction.constants.training_pipeline import SCHEMA_FILE_PATH, TARGET_COLUMN
from gesture_prediction.data_access.data_ingestion_artifact import DataIngestionArtifactData

class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            
            self.data_ingestion_config=data_ingestion_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            self.data_ingestion_artifact_data = DataIngestionArtifactData()
        except Exception as e:
            raise GestureException(e,sys)

    def export_data_into_feature_store(self) -> DataFrame:
        """
        Export mongo db collection record as data frame into feature
        """
        try:
            logging.info("Exporting data from database to feature store")
            Gesture_data = GestureDataCassandra()
            dataframe = Gesture_data.export_collection_as_dataframe(collection_name=self.data_ingestion_config.collection_name)
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path            

            #creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            logging.info("data exported from database to csc")
            return dataframe
        except  Exception as e:
            raise  GestureException(e,sys)

    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        """
        Feature store dataset will be split into train and test file
        """

        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)

            os.makedirs(dir_path, exist_ok=True)

            logging.info(f"Exporting train and test file path.")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            logging.info(f"Exported train and test file path.")
        except Exception as e:
            raise GestureData(e,sys)
    

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            dataframe = self.export_data_into_feature_store()
            dataframe = dataframe.drop(self._schema_config["drop_columns"],axis=1)
            target_null = dataframe[dataframe[TARGET_COLUMN].isna()].index
            dataframe.drop(target_null,inplace=True)
            self.split_data_as_train_test(dataframe=dataframe)
            data_ingestion_artifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.testing_file_path)
            logging.info("saving data ingestion artifact to database")
            self.data_ingestion_artifact_data.save_ingestion_artifact(data_ingestion_artifact=data_ingestion_artifact)
            return data_ingestion_artifact
        except Exception as e:
            raise GestureException(e,sys)