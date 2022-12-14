import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from gesture_prediction.constants.database import NAMESPACE_NAME
from gesture_prediction.constants.environment.variable_key import CASSANDRA_CLIENT_ID,CASSANDRA_CLIENT_SECRET,ASTRA_DB_SECURE_BUNDLE_PATH
from gesture_prediction.logger import logging
from gesture_prediction.constants.database import ASTRA_DB_SECURE_BUNDLE_PATH
import os
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv(CASSANDRA_CLIENT_ID)
CLIENT_SECRET = os.getenv(CASSANDRA_CLIENT_SECRET)





class CassandraSession:
    session = None
    def __init__(self, keyspace_name=NAMESPACE_NAME) -> None:
        try:
            
            if CassandraSession.session is None:
                logging.info("create a cassandra session")
                cloud_config= {
                            'secure_connect_bundle': os.path.join(ASTRA_DB_SECURE_BUNDLE_PATH)
                    }
                auth_provider = PlainTextAuthProvider(CLIENT_ID,CLIENT_SECRET )
                cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
                CassandraSession.session = cluster.connect(keyspace=keyspace_name)
            self.session = CassandraSession.session
            self.keyspace_name = keyspace_name
        except Exception as e:
            raise e