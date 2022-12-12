import os
from gesture_prediction.constants.environment.variable_key import MONGO_DB_URL_ENV_KEY
from dotenv import load_dotenv
load_dotenv()
import argparse
from gesture_prediction.exception import GestureException
import sys,os
from gesture_prediction.logger import logging
from gesture_prediction.pipeline.training_pipeline import TrainPipeline
from gesture_prediction.entity.config_entity import TrainingPipelineConfig

def start_training(start=False):
    try:
        if not start:
            return None
        print("Training Running")
        TrainPipeline().run_pipeline()
        
    except Exception as e:
        raise GestureException(e, sys)


def main(training_status):
    try:

        start_training(start=training_status)
    except Exception as e:
        raise GestureException(e, sys)


if __name__=="__main__":
    main(training_status=True)