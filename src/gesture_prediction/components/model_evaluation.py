
from gesture_prediction.exception import GestureException
from gesture_prediction.logger import logging
from gesture_prediction.entity.artifact_entity import DataValidationArtifact,ModelTrainerArtifact,ModelEvaluationArtifact
from gesture_prediction.entity.config_entity import ModelEvaluationConfig
import os,sys
from gesture_prediction.ml.metric.classification_metric import get_classification_score
from gesture_prediction.ml.model.estimator import GestureModel
from gesture_prediction.utils.main_utils import save_object,load_object,write_yaml_file
from gesture_prediction.ml.model.estimator import ModelResolver
from gesture_prediction.constants.training_pipeline import TARGET_COLUMN
from gesture_prediction.ml.model.estimator import TargetValueMapping
import pandas  as  pd


class ModelEvaluation:


    def __init__(self,model_eval_config:ModelEvaluationConfig,
                    data_validation_artifact:DataValidationArtifact,
                    model_trainer_artifact:ModelTrainerArtifact):
        
        try:
            self.model_eval_config=model_eval_config
            self.data_validation_artifact=data_validation_artifact
            self.model_trainer_artifact=model_trainer_artifact
        except Exception as e:
            raise GestureException(e,sys)
    


    def initiate_model_evaluation(self)->ModelEvaluationArtifact:
        try:
            valid_train_file_path = self.data_validation_artifact.valid_train_file_path
            valid_test_file_path = self.data_validation_artifact.valid_test_file_path

            #valid train and test file dataframe
            train_df = pd.read_csv(valid_train_file_path)
            test_df = pd.read_csv(valid_test_file_path)

            df = pd.concat([train_df,test_df])
            y_true = df[TARGET_COLUMN]
            y_true.replace(TargetValueMapping().to_dict(),inplace=True)
            df.drop(TARGET_COLUMN,axis=1,inplace=True)

            train_model_file_path = self.model_trainer_artifact.trained_model_file_path
            model_resolver = ModelResolver()
            is_model_accepted=True


            if not model_resolver.is_model_exists():
                logging.info("there is no best model available earlier")
                model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=is_model_accepted, 
                    improved_accuracy=None, 
                    best_model_path=None, 
                    trained_model_path=train_model_file_path, 
                    train_model_metric_artifact=self.model_trainer_artifact.test_metric_artifact, 
                    best_model_metric_artifact=None)
                logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
                return model_evaluation_artifact

            latest_model_path = model_resolver.get_best_model_path()
            logging.info("loading previous best model")
            latest_model = load_object(file_path=latest_model_path)
            logging.info("loading newly trained model")
            train_model = load_object(file_path=train_model_file_path)
            
            logging.info("prediction using newly trained model")
            y_trained_pred = train_model.predict(df)

            logging.info("prediction using previous best model")
            y_latest_pred  =latest_model.predict(df)


            
            trained_metric = get_classification_score(y_true, y_trained_pred)
            logging.info(f"classification score as per newly trained model {trained_metric}")

            latest_metric = get_classification_score(y_true, y_latest_pred)
            logging.info(f"classification score as per previous best model {latest_metric}")

            improved_accuracy = trained_metric.f1_score-latest_metric.f1_score
            if self.model_eval_config.change_threshold < improved_accuracy:
                #0.02 < 0.03
                is_model_accepted=True
            else:
                is_model_accepted=False

            
            model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=is_model_accepted, 
                    improved_accuracy=improved_accuracy, 
                    best_model_path=latest_model_path, 
                    trained_model_path=train_model_file_path, 
                    train_model_metric_artifact=trained_metric, 
                    best_model_metric_artifact=latest_metric)

            model_eval_report = model_evaluation_artifact.__dict__

            #save the report
            write_yaml_file(self.model_eval_config.report_file_path, model_eval_report)
            
            return model_evaluation_artifact
            
        except Exception as e:
            raise GestureException(e,sys)

    
    
