from gesture_prediction.entity.artifact_entity import ClassificationMetricArtifact
from gesture_prediction.exception import GestureException
from sklearn.metrics import f1_score,precision_score,recall_score
import os,sys

def get_classification_score(y_true,y_pred)->ClassificationMetricArtifact:
    try:
        model_f1_score = f1_score(y_true, y_pred,average="weighted")
        model_recall_score = recall_score(y_true, y_pred,average="weighted")
        model_precision_score=precision_score(y_true,y_pred,average="weighted")

        classsification_metric =  ClassificationMetricArtifact(f1_score=model_f1_score,
                    precision_score=model_precision_score, 
                    recall_score=model_recall_score)
        return classsification_metric
    except Exception as e:
        raise GestureException(e,sys)