import pandas as pd
from .db_utils import fetch_fashion_data
from .predictor import TrendPredictor, predict_missing_scores
from .forecaster import ForecastAgent, train_forecast, forecast_trends
from .trend_direction import TrendDirectionAgent
import asyncio

# --- Step 1: Regular async wrapper functions with debug ---

async def fetch_data(limit: int = 50):
    print("[DataAgent] Fetching fashion data from DB...")
    df = fetch_fashion_data(limit)
    print(f"[DataAgent] Fetched {len(df)} rows")
    return df

async def predict_scores(df: pd.DataFrame):
    print("[ScorePredictorAgent] Training predictor and filling missing scores...")
    predictor = TrendPredictor().train(df)
    df_filled = predict_missing_scores(df, predictor)
    print("[ScorePredictorAgent] Prediction done.")
    return df_filled

async def forecast_trends_tool(df: pd.DataFrame):
    print("[ForecasterAgent] Training forecast agent and predicting future trends...")
    forecaster = ForecastAgent()
    forecaster = train_forecast(df, forecaster)
    df_forecast = forecast_trends(df, forecaster)
    print("[ForecasterAgent] Forecast completed.")
    return df_forecast

async def compute_direction(df: pd.DataFrame):
    print("[DirectionAgent] Computing trend directions...")
    agent = TrendDirectionAgent()
    df_dir = agent.compute_direction(df, score_column="predicted_trend_score")
    print("[DirectionAgent] Direction computed.")
    return df_dir


def merge(df_main: pd.DataFrame, df_forecast: pd.DataFrame):
    print("[MergeAgent] Merging forecast with main data...")
    df_final = df_main.merge(df_forecast, on="trend_name", how="left")
    df_final["predicted_trend_score"] = df_final["predicted_trend_score"].fillna(0).astype(float)
    df_final["forecasted_trend_score"] = df_final["forecasted_trend_score"].fillna(0).astype(float)

    # Use row-level trend_direction if exists, else 'stable'
    if "trend_direction" in df_final.columns:
        df_final.rename(columns={"trend_direction": "trendDirection"}, inplace=True)
    else:
        df_final["trendDirection"] = "stable"

    df_final["trendDirection"] = df_final["trendDirection"].fillna("stable")
    return df_final


def compute_overall(df_final: pd.DataFrame):
    print("[InsightsAgent] Aggregating overall trend directions...")
    # Use TrendDirectionAgent's static method
    overall = TrendDirectionAgent.compute_overall_direction(
        df_final,
        score_column='predicted_trend_score',
        up_threshold=0.01,
        down_threshold=-0.01
    )
    print("[InsightsAgent] Overall insights computed.")
    return overall


# --- Step 2: Single orchestration function ---
async def run_fashion_trends(limit: int = 50):
    print("[Orchestrator] Starting fashion trend pipeline...")
    df = await fetch_data(limit)
    df = await predict_scores(df)
    df_forecast = await forecast_trends_tool(df)
    df = await compute_direction(df)
    df_final = merge(df, df_forecast)
    df_overall = compute_overall(df_final)
    print("[Orchestrator] Pipeline complete.")
    return df_final, df_overall
