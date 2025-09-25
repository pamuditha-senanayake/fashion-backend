from sklearn.ensemble import RandomForestRegressor
import pandas as pd


class TrendPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def train(self, df: pd.DataFrame):
        # feature engineering
        df['content_length'] = df['content'].str.len()
        df['num_hashtags'] = df['hashtags'].apply(len)
        df['num_tags'] = df['tags'].apply(len)

        features = ['likes', 'shares', 'comments', 'content_length', 'num_hashtags', 'num_tags']
        X = df[features]
        y = df['trend_score']
        self.model.fit(X, y)
        return self

    def predict(self, df: pd.DataFrame):
        df['content_length'] = df['content'].str.len()
        df['num_hashtags'] = df['hashtags'].apply(len)
        df['num_tags'] = df['tags'].apply(len)

        features = ['likes', 'shares', 'comments', 'content_length', 'num_hashtags', 'num_tags']
        X = df[features]
        df['predicted_trend_score'] = self.model.predict(X)
        return df
