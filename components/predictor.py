# backend/components/predictor.py
from sklearn.ensemble import RandomForestRegressor

class TrendPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def train(self, df):
        df['content_length'] = df['content'].str.len()
        df['num_hashtags'] = df['hashtags'].apply(len)
        df['num_tags'] = df['tags'].apply(len)
        features = ['likes','shares','comments','content_length','num_hashtags','num_tags']
        self.model.fit(df[features], df['trend_score'])
        return self

def predict_missing_scores(df, predictor):
    mask = df['trend_score'].isnull()
    if mask.sum() > 0:
        df_missing = df[mask].copy()
        df_missing['content_length'] = df_missing['content'].str.len()
        df_missing['num_hashtags'] = df_missing['hashtags'].apply(len)
        df_missing['num_tags'] = df_missing['tags'].apply(len)
        features = ['likes','shares','comments','content_length','num_hashtags','num_tags']
        df.loc[mask, 'trend_score'] = predictor.model.predict(df_missing[features])
    df['predicted_trend_score'] = df['trend_score']
    return df
