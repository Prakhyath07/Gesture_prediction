from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    trained_file_path: str
    test_file_path: str

    def to_dict(self):
        return self.__dict__

@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

    def to_dict(self):
        return self.__dict__

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str

    def to_dict(self):
        return self.__dict__

@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float

    def to_dict(self):
        return self.__dict__

@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact

    def _asdict(self):
        try:
            response = dict()
            response['trained_model_file_path'] = self.trained_model_file_path
            response['model_trainer_train_metric_artifact'] = self.train_metric_artifact.to_dict()
            response['model_trainer_test_metric_artifact'] = self.test_metric_artifact.to_dict()
            return response
        except Exception as e:
            raise e

@dataclass
class ModelEvaluationArtifact:
    is_model_accepted: bool
    improved_accuracy: float
    best_model_path: str
    trained_model_path: str
    train_model_metric_artifact: ClassificationMetricArtifact
    best_model_metric_artifact: ClassificationMetricArtifact

    def to_dict(self):
        try:
            response = dict()
            response['is_model_accepted'] = self.is_model_accepted
            response['improved_accuracy'] = self.improved_accuracy
            response['best_model_path'] = self.best_model_path
            response['trained_model_path'] = self.trained_model_path
            response['model_evaluation_train_model_metric_artifact'] = self.train_model_metric_artifact.to_dict()
            response['model_evaluation_best_model_metric_artifact'] = self.best_model_metric_artifact.to_dict()
            return response
        except Exception as e:
            raise e

@dataclass
class ModelPusherArtifact:
    saved_model_path:str
    model_file_path:str

    def to_dict(self):
        return self.__dict__


@dataclass
class PredictionArtifact:
    input_file_path: str
    prediction_file_path: str

    def to_dict(self):
        return self.__dict__