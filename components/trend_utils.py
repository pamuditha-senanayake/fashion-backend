# components/trend_utils.py

from .db_utils import fetch_trend_over_time
import pandas as pd

def get_trend_popularity_over_time(trend_names: str = None, limit: int = 500):
    """
    Returns trend popularity over time as a list of dicts.
    Optional: trend_names is a comma-separated string of trend names to filter.
    """
    # Fetch data from db.py (returns DataFrame)
    df = fetch_trend_over_time(limit=limit)

    # Filter by trend_names if provided
    if trend_names:
        names = [name.strip() for name in trend_names.split(",")]
        df = df[df['trend_name'].isin(names)]

    # Ensure proper sorting: by trend_name and timestamp ascending
    if 'timestamp' in df.columns:
        df = df.sort_values(by=['trend_name', 'timestamp'])
    else:
        df = df.sort_values(by=['trend_name'])

    # Prepare for API: convert timestamp to ISO string if exists
    if 'timestamp' in df.columns:
        df['timestamp'] = df['timestamp'].apply(lambda x: x.isoformat() if not pd.isna(x) else None)

    # Convert DataFrame to list of dicts
    result = df.to_dict(orient="records")
    return result
