# backend/components/forecaster.py
from sklearn.ensemble import RandomForestRegressor

class ForecastAgent:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def prepare_features(self, df):
        df = df.sort_values(by=['trend_name', 'timestamp'])
        df['prev_score'] = df.groupby('trend_name')['trend_score'].shift(1)
        df['prev_score2'] = df.groupby('trend_name')['trend_score'].shift(2)
        df['prev_score3'] = df.groupby('trend_name')['trend_score'].shift(3)
        df['rolling_mean'] = df.groupby('trend_name')['trend_score'].transform(
            lambda x: x.rolling(3, min_periods=1).mean())
        df['rolling_std'] = df.groupby('trend_name')['trend_score'].transform(
            lambda x: x.rolling(3, min_periods=1).std().fillna(0))
        df = df.fillna(0)
        return df

def train_forecast(df, agent):
    df = agent.prepare_features(df)
    features = ['prev_score','prev_score2','prev_score3','likes','shares','comments','rolling_mean','rolling_std']
    agent.model.fit(df[features], df['trend_score'])
    return agent

def forecast_trends(df, agent):
    df = agent.prepare_features(df)
    features = ['prev_score','prev_score2','prev_score3','likes','shares','comments','rolling_mean','rolling_std']
    df['forecasted_trend_score'] = agent.model.predict(df[features])
    return df[['trend_name','forecasted_trend_score']]
