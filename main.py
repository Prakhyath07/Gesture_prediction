import os
from gesture_prediction.constants.environment.variable_key import MONGO_DB_URL_ENV_KEY
from dotenv import load_dotenv
load_dotenv()
import argparse
from gesture_prediction.exception import GestureException
import sys,os
from gesture_prediction.logger import logging
from gesture_prediction.pipeline.training_pipeline import TrainPipeline
from gesture_prediction.pipeline.prediction_pipeline import PredictPipeline
from fastapi import FastAPI, UploadFile
from gesture_prediction.constants.application import APP_HOST, APP_PORT
from starlette.responses import RedirectResponse, Response
from uvicorn import run as app_run
from gesture_prediction.utils.main_utils import load_object
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:

        train_pipeline = TrainPipeline()
        if TrainPipeline.is_pipeline_running:
            return Response("Training pipeline is already running.")
        train_pipeline.run_pipeline()
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")

class results(BaseModel):
    idx : int
    prediction: int

@app.post("/predict",response_model=List[results])
async def predict_route(file: UploadFile):
    try:
        
        #get data from user csv file
        #conver csv file to dataframe
        cont =await file.read()
        predictpipeline =PredictPipeline(cont,time=datetime.now())
        #decide how to return file to user.
        pred_artifact = predictpipeline.run_pipeline()
        df = pd.read_csv(pred_artifact.prediction_file_path)
        a= [results(idx = i, prediction=df.iloc[i,-1]) for i in range(df.shape[0])]
        print(a)
        return a
        
    except Exception as e:
        raise Response(e)


def start_training(start=False):
    try:
        if not start:
            return None
        print("Training Running")
        TrainPipeline().run_pipeline()
        
    except Exception as e:
        raise GestureException(e, sys)

def start_prediction(start=False):
    try:
        if not start:
            return None
        print("Prediction Running")
        PredictPipeline().run_pipeline()
        
    except Exception as e:
        raise GestureException(e, sys)

def main(training_status):
    try:

        start_training(start=training_status)
    except Exception as e:
        raise GestureException(e, sys)


if __name__=="__main__":
    # main(training_status=True)
    app_run(app, host=APP_HOST, port=APP_PORT)