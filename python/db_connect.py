import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path= os.environ["DATABRICKS_HTTP_PATH"],
        access_token= os.environ["DATABRICKS_TOKEN"],
    )

def query_df(query: str) -> pd.DataFrame:
    """Run a SQL query against Databricks and return a pandas DataFrame."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)