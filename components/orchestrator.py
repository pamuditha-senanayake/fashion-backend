#%%
import os
import pandas as pd
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, trace
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

from .db_utils import fetch_fashion_data
from .predictor import TrendPredictor, predict_missing_scores
from .forecaster import ForecastAgent, train_forecast, forecast_trends
from .trend_direction import TrendDirectionAgent, compute_overall_direction

#%%
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize OpenAI / Gemini client
gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_API_KEY
)

#%%
# Wrap existing pipeline functions as tools

@function_tool
def data_agent(limit: int = 50) -> pd.DataFrame:
    """Fetch fashion data"""
    df = fetch_fashion_data(limit)
    return df

@function_tool
def score_predictor_agent(df: pd.DataFrame) -> pd.DataFrame:
    """Train predictor and fill missing scores"""
    predictor = TrendPredictor().train(df)
    df_filled = predict_missing_scores(df, predictor)
    return df_filled

@function_tool
def forecaster_agent(df: pd.DataFrame) -> pd.DataFrame:
    """Train forecast agent and predict"""
    forecaster = ForecastAgent()
    forecaster = train_forecast(df, forecaster)
    df_forecast = forecast_trends(df, forecaster)
    return df_forecast

@function_tool
def direction_agent(df: pd.DataFrame) -> pd.DataFrame:
    """Compute trend directions"""
    agent = TrendDirectionAgent()
    df_dir = agent.compute_direction(df, score_column="predicted_trend_score")
    return df_dir

@function_tool
def insights_agent(df_final: pd.DataFrame) -> dict:
    """Compute overall insights"""
    return compute_overall_direction(df_final)

#%%
# Define agents for each step
data_agent_ai = Agent(
    name="DataAgent",
    instructions="Fetch fashion data from DB and return as DataFrame.",
    tools=[data_agent],
    model="gpt-4o-mini"
)

score_agent_ai = Agent(
    name="ScorePredictorAgent",
    instructions="Train predictor, fill missing trend scores.",
    tools=[score_predictor_agent],
    model="gpt-4o-mini"
)

forecast_agent_ai = Agent(
    name="ForecasterAgent",
    instructions="Forecast future trend scores.",
    tools=[forecaster_agent],
    model="gpt-4o-mini"
)

direction_agent_ai = Agent(
    name="DirectionAgent",
    instructions="Compute trend directions based on predicted scores.",
    tools=[direction_agent],
    model="gpt-4o-mini"
)

insights_agent_ai = Agent(
    name="InsightsAgent",
    instructions="Compute overall insights and trends.",
    tools=[insights_agent],
    model="gpt-4o-mini"
)

#%%
# High-level orchestrator agent
instructions_manager = """
You are FashionManager. Your goal is to orchestrate the entire fashion trend pipeline.
1. Use DataAgent to fetch data.
2. Use ScorePredictorAgent to fill missing scores.
3. Use ForecasterAgent to forecast trends.
4. Use DirectionAgent to compute directions.
5. Use InsightsAgent to compute overall insights.
6. Aggregate results for frontend, ensuring proper columns are returned.
"""

tools = [data_agent_ai.as_tool(), score_agent_ai.as_tool(),
         forecast_agent_ai.as_tool(), direction_agent_ai.as_tool(),
         insights_agent_ai.as_tool()]

FashionManager = Agent(
    name="FashionManager",
    instructions=instructions_manager,
    tools=tools,
    model="gpt-4o-mini"
)

#%%
# Orchestrator runner
async def run_fashion_trends_agentic(limit: int = 50):
    message = f"Run full fashion trend pipeline for limit={limit}"
    with trace("FashionManager Pipeline"):
        result = await Runner.run(FashionManager, message)
    return result.final_output
