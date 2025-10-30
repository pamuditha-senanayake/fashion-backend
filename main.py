# backend/main.py
import os
from dotenv import load_dotenv
import asyncio
import json
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner
from starlette.staticfiles import StaticFiles

from components import gallery_agent
from components.orchestrator2 import run_fashion_trends
from components.responsible_ai_agent import ResponsibleAIAgent
from components.fashion_ai import FashionAI
from components.trend_direction import TrendDirectionAgent  # <- added import
from components.trend_utils import get_trend_popularity_over_time

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
app.include_router(gallery_agent.router)
print("Gallery router included.")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


@app.get("/search")
async def search_stream(query: str = Query(...)):
    async def event_stream():
        yield f"data: {json.dumps({'status': 'Thinking...'})}\n\n"
        await asyncio.sleep(0.5)

        # Streaming runner — DO NOT await
        result = Runner.run_streamed(fashion_ai.fashion_manager, input=query)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield f"data: {json.dumps({'status': 'Streaming', 'delta': event.data.delta})}\n\n"

        yield f"data: {json.dumps({'status': 'Done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/predict_trends_full")
async def predict_trends_full(limit: int = 20):
    try:
        # Use the single orchestration function
        df_final, _ = await run_fashion_trends(limit=limit)

        # Compute overall trend directions using TrendDirectionAgent
        agent = TrendDirectionAgent()
        df_overall = agent.compute_overall_direction(df_final, score_column='forecasted_trend_score',
                                                     up_threshold=0.01, down_threshold=-0.01)

        # Merge overall directions back to df_final for frontend
        df_final = df_final.groupby('trend_name').agg({
            'content': 'first',
            'hashtags': 'first',
            'predicted_trend_score': 'mean',
            'forecasted_trend_score': 'mean'
        }).reset_index()

        df_final = pd.merge(df_final, df_overall[['trend_name', 'trendDirection']], on='trend_name', how='left')

        # Fill missing values and normalize types
        df_final['predicted_trend_score'] = df_final['predicted_trend_score'].fillna(0.0).astype(float)
        df_final['forecasted_trend_score'] = df_final['forecasted_trend_score'].fillna(0.0).astype(float)
        df_final['content'] = df_final['content'].fillna('No description')
        df_final['trendDirection'] = df_final['trendDirection'].fillna('stable')
        df_final['hashtags'] = df_final['hashtags'].apply(lambda x: x if isinstance(x, list) else [])

        # print("values", df_final['trendDirection'])
        return df_final.to_dict(orient='records')

    except Exception as e:
        print(f"Error in /predict_trends_full: {e}")
        return {"error": str(e)}


# --- Pydantic models ---
class TrendItem(BaseModel):
    trend_name: str
    content: str = ""
    hashtags: List[str] = []
    predicted_trend_score: float = 0.0
    forecasted_trend_score: float = 0.0
    trendDirection: str = "stable"


class AuditRequest(BaseModel):
    trends: List[TrendItem]



# --- Fixed endpoint for frontend sending { trends: [...] } ---
@app.post("/audit_trends")
async def audit_trends(request: AuditRequest):
    print("[DEBUG] Received request:", request)
    print("[DEBUG] Type of request.trends:", type(request.trends))
    try:
        if not request.trends:
            return {"error": "No trends provided for auditing."}

        df = pd.DataFrame([t.dict() for t in request.trends])
        print("[DEBUG] Converted DataFrame:\n", df)

        ai_auditor = ResponsibleAIAgent()
        df_audit = await ai_auditor.audit_trends(df)

        return df_audit.fillna("").to_dict(orient='records')

    except Exception as e:
        print("[ERROR] Exception in /audit_trends:", e)
        return {"error": str(e)}

@app.get("/trend_popularity_over_time")
def trend_popularity(trend_names: str = None):
    return get_trend_popularity_over_time(trend_names)

