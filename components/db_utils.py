# backend/components/db_utils.py
import pandas as pd
from sqlalchemy import create_engine

DB_USER = "pamudithasenanayake"
DB_PASS = "123"
DB_HOST = "localhost"
DB_NAME = "fashionsite"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

def fetch_fashion_data(limit=100):
    df = pd.read_sql(f"SELECT * FROM synthetic_fashion_trends ORDER BY timestamp DESC LIMIT {limit}", engine)
    df['hashtags'] = df['hashtags'].apply(lambda x: list(x) if x else [])
    df['tags'] = df['tags'].apply(lambda x: list(x) if x else [])
    # add slight noise to avoid identical trend scores
    import numpy as np
    df['trend_score'] = df['trend_score'] + np.random.uniform(-0.05, 0.05, size=len(df))
    df['trend_score'] = df['trend_score'].clip(0,1)
    return df
