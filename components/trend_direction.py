import pandas as pd

class TrendDirectionAgent:
    """
    Computes the direction of each trend over time using predicted and forecasted scores.
    """
    def __init__(self, threshold=0.001):
        # threshold: minimum change to consider as up/down
        self.threshold = threshold

    def compute_direction(self, df, score_column='predicted_trend_score'):
        """
        Adds a 'trend_direction' column based on score change over time per trend.
        """
        df = df.sort_values(by=['trend_name', 'timestamp'])
        df['prev_score'] = df.groupby('trend_name')[score_column].shift(1)
        df['score_change'] = df[score_column] - df['prev_score']

        def get_direction(x):
            if pd.isna(x):
                return 'stable'
            if x > self.threshold:
                return 'up'
            elif x < -self.threshold:
                return 'down'
            else:
                return 'stable'

        df['trend_direction'] = df['score_change'].apply(get_direction)
        df['trend_direction'] = df['trend_direction'].fillna('stable')
        return df


def compute_overall_direction(df, predicted_col='predicted_trend_score',
                              forecast_col='forecasted_trend_score', threshold=0.001):
    """
    Computes overall trend per trend_name using first vs last forecasted-predicted difference.
    """
    df_grouped = df.groupby('trend_name').agg({
        predicted_col: 'mean',
        forecast_col: 'mean',
        'timestamp': ['min','max']
    }).reset_index()

    df_grouped.columns = ['trend_name', predicted_col, forecast_col, 'start_time', 'end_time']

    # Get first and last predicted & forecast scores
    first_last = df.sort_values(['trend_name','timestamp']).groupby('trend_name').agg({
        predicted_col: ['first','last'],
        forecast_col: ['first','last']
    }).reset_index()
    first_last.columns = ['trend_name', 'pred_first','pred_last','fc_first','fc_last']

    # Change over time
    first_last['score_change'] = first_last['fc_last'] - first_last['pred_first']

    def get_direction(x):
        if x > threshold:
            return 'up'
        elif x < -threshold:
            return 'down'
        else:
            return 'stable'

    first_last['trend_direction'] = first_last['score_change'].apply(get_direction)

    # Merge with aggregated scores
    df_final = df_grouped.merge(first_last[['trend_name','trend_direction']], on='trend_name', how='left')
    return df_final[['trend_name', predicted_col, forecast_col, 'trend_direction']]
