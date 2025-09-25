import os
import asyncio
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner
from components.db_utils import fetch_fashion_data
from components.predictor import TrendPredictor, predict_missing_scores
from components.forecaster import ForecastAgent, train_forecast, forecast_trends
from components.trend_direction import TrendDirectionAgent, compute_overall_direction


# Import modular components

from components.fashion_ai import FashionAI


# Load environment variables
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize components
fashion_ai = FashionAI(GEMINI_API_KEY)



# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/search")
async def search_stream(query: str = Query(...)):
    async def event_stream():
        yield f"data: {json.dumps({'status': 'Thinking...'})}\n\n"
        await asyncio.sleep(0.5)

        # Streaming runner — DO NOT await
        result = Runner.run_streamed(fashion_ai.agent, input=query)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield f"data: {json.dumps({'status': 'Streaming', 'delta': event.data.delta})}\n\n"

        yield f"data: {json.dumps({'status': 'Done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/predict_trends")
def get_trends(limit: int = 20):
    df = fetch_fashion_data(limit=limit)
    predictor = TrendPredictor().train(df)
    df = predict_missing_scores(df, predictor)
    forecast_agent = ForecastAgent()
    forecast_agent = train_forecast(df, forecast_agent)
    df_forecast = forecast_trends(df, forecast_agent)
    direction_agent = TrendDirectionAgent()
    df = direction_agent.compute_direction(df, score_column='predicted_trend_score')
    df_final = df.merge(df_forecast, on='trend_name', how='left')
    df_overall = compute_overall_direction(df_final)
    # Convert to dict for JSON
    return df_overall.to_dict(orient='records')