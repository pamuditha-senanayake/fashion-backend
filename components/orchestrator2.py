import pandas as pd
from .db_utils import fetch_fashion_data
from .predictor import TrendPredictor, predict_missing_scores
from .forecaster import ForecastAgent, train_forecast, forecast_trends
from .trend_direction import TrendDirectionAgent, compute_overall_direction
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
    df_final["trendDirection"] = df_final.get("trend_direction", "stable").fillna("stable")
    print("[MergeAgent] Merge completed.")
    return df_final

def compute_overall(df_final: pd.DataFrame):
    print("[InsightsAgent] Aggregating overall trend directions...")
    overall = compute_overall_direction(df_final)
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

# import pandas as pd
# from .db_utils import fetch_fashion_data
# from .predictor import TrendPredictor, predict_missing_scores
# from .forecaster import ForecastAgent, train_forecast, forecast_trends
# from .trend_direction import TrendDirectionAgent, compute_overall_direction
# import os
# from dotenv import load_dotenv
# from agents import Runner, Agent, OpenAIChatCompletionsModel
# from openai import AsyncOpenAI
# import numpy as np
#
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
#
#
# class FashionTrendOrchestrator:
#     def __init__(self, gemini_api_key: str):
#         self.gemini_client = AsyncOpenAI(
#             base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#             api_key=gemini_api_key
#         )
#         self.gemini_model = OpenAIChatCompletionsModel(
#             model="gemini-2.0-flash",
#             openai_client=self.gemini_client
#         )
#         instructions = (
#             "You are the Fashion Trend Orchestrator. "
#             "You coordinate the pipeline agents: DataAgent, ScorePredictorAgent, "
#             "ForecasterAgent, DirectionAgent, InsightsAgent. "
#             "Before calling each agent/tool, briefly explain the step. "
#             "Finally, provide the aggregated trends with predicted, forecasted scores, and trend direction."
#         )
#         self.agent = Agent(
#             name="Gemini Fashion Orchestrator",
#             instructions=instructions,
#             model=self.gemini_model
#         )
#
#     async def run_pipeline(self, limit=50):
#         # Step 1: Fetch Data
#         print("[DataAgent] Fetching fashion data from DB...")
#         df = fetch_fashion_data(limit)
#
#         # Step 2: Train Predictor & Fill Missing Scores
#         print("[ScorePredictorAgent] Training predictor and filling missing scores...")
#         predictor_agent = TrendPredictor().train(df)
#         df = predict_missing_scores(df, predictor_agent)
#
#         # Step 3: Train Forecaster & Predict
#         print("[ForecasterAgent] Training forecast agent and predicting future trends...")
#         forecast_agent = ForecastAgent()
#         forecast_agent = train_forecast(df, forecast_agent)
#         df_forecast = forecast_trends(df, forecast_agent)
#
#         # Step 4: Compute Trend Directions
#         print("[DirectionAgent] Computing trend directions...")
#         direction_agent = TrendDirectionAgent()
#         df = direction_agent.compute_direction(df, score_column='predicted_trend_score')
#
#         # Step 5: Merge Forecast & Direction
#         df_final = df.merge(df_forecast, on='trend_name', how='left')
#
#         # Step 6: Compute Overall Direction
#         print("[InsightsAgent] Aggregating overall trend directions...")
#         df_overall = compute_overall_direction(df_final)
#
#         # --- Ensure frontend-ready fields ---
#         df_final['predicted_trend_score'] = df_final['predicted_trend_score'].fillna(0).astype(float)
#         df_final['forecasted_trend_score'] = df_final['forecasted_trend_score'].fillna(0).astype(float)
#
#         # Normalize direction column for frontend
#         if 'trend_direction' in df_final.columns:
#             df_final.rename(columns={'trend_direction': 'trendDirection'}, inplace=True)
#         else:
#             df_final['trendDirection'] = 'stable'
#
#         df_final['trendDirection'] = df_final['trendDirection'].fillna('stable')
#
#         return df_final, df_overall
