# backend/components/trend_direction.py
class TrendDirectionAgent:
    def __init__(self, up_threshold=0.01, down_threshold=-0.01):
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold

    def compute_direction(self, df, score_column='trend_score'):
        df = df.sort_values(by=['trend_name','timestamp'])
        df['prev_score'] = df.groupby('trend_name')[score_column].shift(1)
        df['score_change'] = df[score_column] - df['prev_score']
        df['trend_direction'] = df['score_change'].apply(
            lambda x: 'up' if x > self.up_threshold else ('down' if x < self.down_threshold else 'stable')
        )
        df['trend_direction'] = df['trend_direction'].fillna('stable')
        return df

def compute_overall_direction(df, predicted_col='predicted_trend_score', forecast_col='forecasted_trend_score',
                              up_threshold=0.01, down_threshold=-0.01):
    agg = df.groupby('trend_name').agg({predicted_col:'mean', forecast_col:'mean'}).reset_index()
    agg['score_change'] = agg[forecast_col] - agg[predicted_col]
    agg['trend_direction'] = agg['score_change'].apply(
        lambda x: 'up' if x > up_threshold else ('down' if x < down_threshold else 'stable')
    )
    return agg[['trend_name', predicted_col, forecast_col, 'trend_direction']]
