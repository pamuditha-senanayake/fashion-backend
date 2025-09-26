# backend/components/forecaster.py
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class ForecastAgent:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds lag features, rolling mean/std, and fills NaNs safely.
        """
        df = df.sort_values(by=['trend_name', 'timestamp'])

        # Lag features
        df['prev_score'] = df.groupby('trend_name')['trend_score'].shift(1)
        df['prev_score2'] = df.groupby('trend_name')['trend_score'].shift(2)
        df['prev_score3'] = df.groupby('trend_name')['trend_score'].shift(3)

        # Rolling statistics
        df['rolling_mean'] = df.groupby('trend_name')['trend_score'].transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
        df['rolling_std'] = df.groupby('trend_name')['trend_score'].transform(
            lambda x: x.rolling(3, min_periods=1).std().fillna(0)
        )

        # Fill remaining NaNs and ensure proper dtypes
        df = df.fillna(0).infer_objects()
        return df

def train_forecast(df: pd.DataFrame, agent: ForecastAgent) -> ForecastAgent:
    """
    Train the forecast agent model on prepared features.
    """
    df = agent.prepare_features(df)
    features = [
        'prev_score','prev_score2','prev_score3',
        'likes','shares','comments','rolling_mean','rolling_std'
    ]
    agent.model.fit(df[features], df['trend_score'])
    return agent

def forecast_trends(df: pd.DataFrame, agent: ForecastAgent) -> pd.DataFrame:
    """
    Predict future trend scores and return a dataframe with forecasted values.
    """
    df = agent.prepare_features(df)
    features = [
        'prev_score','prev_score2','prev_score3',
        'likes','shares','comments','rolling_mean','rolling_std'
    ]
    df['forecasted_trend_score'] = agent.model.predict(df[features])

    # Ensure no NaNs in forecasted scores
    df['forecasted_trend_score'] = df['forecasted_trend_score'].fillna(0)
    return df[['trend_name','forecasted_trend_score']]
