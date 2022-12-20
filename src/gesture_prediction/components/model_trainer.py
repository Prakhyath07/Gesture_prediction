
from gesture_prediction.utils.main_utils import load_numpy_array_data
from gesture_prediction.exception import GestureException
from gesture_prediction.logger import logging
from gesture_prediction.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from gesture_prediction.entity.config_entity import ModelTrainerConfig
import os,sys
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from gesture_prediction.ml.metric.classification_metric import get_classification_score
from gesture_prediction.ml.model.estimator import GestureModel
from gesture_prediction.utils.main_utils import save_object,load_object
from gesture_prediction.data_access.model_trainer_artifact import ModelTrainerArtifactData

class ModelTrainer:

    def __init__(self,model_trainer_config:ModelTrainerConfig,
        data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
            self.model_trainer_artifact_data = ModelTrainerArtifactData()

        except Exception as e:
            raise GestureException(e,sys)

    def perform_hyper_paramter_tunig(self):...
    

    def train_model(self,x_train,y_train):
        try:
            logging.info("fitting data to xgboost classifier")
            xgb_clf = XGBClassifier()
            xgb_clf.fit(x_train,y_train)
            return xgb_clf
            # logging.info("fitting data to randomforest classifier")
            # rf_clf = RandomForestClassifier(class_weight='balanced', max_depth=7)
            # rf_clf.fit(x_train,y_train)
            # return rf_clf
            # logging.info("fitting data to extra tree classifier")
            # et_clf = ExtraTreesClassifier(7)
            # et_clf.fit(x_train,y_train)
            # return et_clf
        except Exception as e:
            raise e
    
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)
            logging.info("splitting feature and target variables")
            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model = self.train_model(x_train, y_train)
            logging.info("predicting train target variable")
            y_train_pred = model.predict(x_train)
            classification_train_metric =  get_classification_score(y_true=y_train, y_pred=y_train_pred)
            logging.info(f"classification score for training set {classification_train_metric}")
            if classification_train_metric.f1_score<=self.model_trainer_config.expected_accuracy:
                raise Exception("Trained model is not good to provide expected accuracy")
            
            logging.info("predicting test target variable")
            y_test_pred = model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"classification score for testing set {classification_test_metric}")

            #Overfitting and Underfitting
            diff = abs(classification_train_metric.f1_score-classification_test_metric.f1_score)
            
            if diff>self.model_trainer_config.overfitting_underfitting_threshold:
                raise Exception("Model is not good try to do more experimentation.")
            logging.info(f"difference between train and test classification score: {diff}")
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path,exist_ok=True)
            Gesture_model = GestureModel(preprocessor=preprocessor,model=model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=Gesture_model)

            #model trainer artifact

            model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path, 
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric)
            logging.info("saving model trainer artifact to database")
            self.model_trainer_artifact_data.save_trainer_artifact(model_trainer_artifact=model_trainer_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise GestureException(e,sys)