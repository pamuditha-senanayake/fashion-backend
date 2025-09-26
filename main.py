# backend/main.py
import os
from dotenv import load_dotenv
import asyncio
import json
import pandas as pd
import numpy as np  # <- added for NaN handling
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner
from starlette.staticfiles import StaticFiles

from components import gallery_agent
from components.orchestrator import FashionTrendOrchestrator
from components.responsible_ai_agent import ResponsibleAIAgent
from components.fashion_ai import FashionAI

# Load environment variables
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize components
fashion_ai = FashionAI(GEMINI_API_KEY)
orchestrator = FashionTrendOrchestrator(gemini_api_key=GEMINI_API_KEY)


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
        result = Runner.run_streamed(fashion_ai.agent, input=query)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield f"data: {json.dumps({'status': 'Streaming', 'delta': event.data.delta})}\n\n"

        yield f"data: {json.dumps({'status': 'Done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/predict_trends_full")
async def predict_trends_full(limit: int = 20):
    try:
        # Run the orchestrator pipeline
        df_final, _ = await orchestrator.run_pipeline(limit=limit)

        # Keep only one row per trend_name for frontend
        df_final = df_final.groupby('trend_name').agg({
            'content': 'first',
            'hashtags': 'first',
            'predicted_trend_score': 'mean',
            'forecasted_trend_score': 'mean',
            'trendDirection': 'first'
        }).reset_index()

        # Ensure no NaNs and proper types
        df_final['predicted_trend_score'] = df_final['predicted_trend_score'].fillna(0.0).astype(float)
        df_final['forecasted_trend_score'] = df_final['forecasted_trend_score'].fillna(0.0).astype(float)
        df_final['content'] = df_final['content'].fillna('No description')
        df_final['trendDirection'] = df_final['trendDirection'].fillna('stable')
        df_final['hashtags'] = df_final['hashtags'].apply(lambda x: x if isinstance(x, list) else [])

        # Return JSON-safe dictionary
        return df_final.to_dict(orient='records')

    except Exception as e:
        return {"error": str(e)}

# backend/main.py (excerpt)
@app.get("/trends_with_audit")
async def trends_with_audit(limit: int = 50):
    try:
        # Use orchestrator to get consolidated trend data
        orchestrator_instance = FashionTrendOrchestrator(GEMINI_API_KEY)
        df_final, _ = await orchestrator_instance.run_pipeline(limit=limit)

        # Run Responsible AI auditing
        ai_auditor = ResponsibleAIAgent()
        df_audit = await ai_auditor.audit_trends(df_final)

        # JSON-safe return
        return df_audit.fillna("").to_dict(orient='records')

    except Exception as e:
        print("Error in /trends_with_audit:", e)
        return {"error": str(e)}