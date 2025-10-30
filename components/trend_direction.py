import pandas as pd

class TrendDirectionAgent:
    """
    Computes trend directions per row and overall trend per trend_name.
    """
    def __init__(self, threshold: float = 0.001):
        self.threshold = threshold

    def compute_direction(self, df: pd.DataFrame, score_column: str = 'predicted_trend_score'):
        """
        Compute row-level trend direction (change from previous timestamp).
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

    @staticmethod
    def compute_overall_direction(df: pd.DataFrame, score_column='forecasted_trend_score',
                                  up_threshold=0.01, down_threshold=-0.01):
        """
        Compute overall trend per trend_name using first vs last forecasted score.
        """
        first_last = (
            df.sort_values(['trend_name', 'timestamp'])
              .groupby('trend_name')
              .agg({score_column: ['first', 'last']})
              .reset_index()
        )
        first_last.columns = ['trend_name', 'score_first', 'score_last']

        first_last['score_change'] = first_last['score_last'] - first_last['score_first']

        def get_direction(x):
            # print(x)
            if x > up_threshold:
                return 'up'
            elif x < down_threshold:
                return 'down'
            else:
                return 'stable'

        first_last['trendDirection'] = first_last['score_change'].apply(get_direction)
        return first_last[['trend_name', 'score_first', 'score_last', 'trendDirection']]
