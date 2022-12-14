import sys
from typing import Optional

import numpy as np
import pandas as pd

from gesture_prediction.configuration.mongodb_connection import MongoDBClient
from gesture_prediction.configuration.Cassandra_connection import CassandraSession
from gesture_prediction.constants.database import DATABASE_NAME,NAMESPACE_NAME
from gesture_prediction.exception import GestureException


class GestureData:
    """
    This class help to export entire mongo db record as pandas dataframe
    """

    def __init__(self):
        """
        """
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)

        except Exception as e:
            raise GestureException(e, sys)

    def export_collection_as_dataframe(
        self, collection_name: str, database_name: Optional[str] = None) -> pd.DataFrame:
        try:
            """
            export entire collectin as dataframe:
            return pd.DataFrame of collection
            """
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]
            df = pd.DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise GestureException(e, sys)


class GestureDataCassandra:
    """
    This class help to export entire mongo db record as pandas dataframe
    """

    def __init__(self):
        """
        """
        try:
            self.cassandra_sess = CassandraSession(keyspace_name=NAMESPACE_NAME).session

        except Exception as e:
            raise GestureException(e, sys)

    def export_collection_as_dataframe(
        self, collection_name: str) -> pd.DataFrame:
        try:
            """
            export entire collectin as dataframe:
            return pd.DataFrame of collection
            """
            collection = self.cassandra_sess.execute(f"select * from {collection_name}")
            df = pd.DataFrame(list(collection.all()))

            if "id" in df.columns.to_list():
                df = df.drop(columns=["id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise GestureException(e, sys)