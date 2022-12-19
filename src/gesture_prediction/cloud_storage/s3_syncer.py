
import os, sys
from gesture_prediction.logger import logging
from gesture_prediction.exception import GestureException

class S3Sync:


    def sync_folder_to_s3(self,folder,aws_bucket_url):
        try:
            logging.info(f"syncing {folder} to s3")
            command = f"aws s3 sync {folder} {aws_bucket_url} "
            os.system(command)
        except Exception as e:
            raise GestureException(e,sys)

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        try:
            logging.info(f"syncing {folder} from s3")
            command = f"aws s3 sync  {aws_bucket_url} {folder} "
            os.system(command)
        except Exception as e:
            raise GestureException(e,sys)


