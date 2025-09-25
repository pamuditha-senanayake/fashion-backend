import pandas as pd
from sqlalchemy import create_engine
import os

DB_USER = "pamudithasenanayake"
DB_PASS = "123"
DB_HOST = "localhost"
DB_NAME = "fashionsite"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def fetch_fashion_data(limit=100):
    query = "SELECT * FROM synthetic_fashion_trends ORDER BY timestamp DESC LIMIT %s"
    df = pd.read_sql(query, engine, params=(limit,))
    df['hashtags'] = df['hashtags'].apply(lambda x: list(x) if x else [])
    df['tags'] = df['tags'].apply(lambda x: list(x) if x else [])
    return df
