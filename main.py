import os
import asyncio
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner

# Import modular components
from components.db_fashion import fetch_fashion_data
from components.trend_predictor import TrendPredictor
from components.fashion_ai import FashionAI

# Load environment variables
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize components
fashion_ai = FashionAI(GEMINI_API_KEY)
trend_model = TrendPredictor()

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/fashion_posts")
async def get_fashion_posts(limit: int = 50):
    """
    Fetch recent fashion posts from PostgreSQL.
    """
    df = fetch_fashion_data(limit)
    return df.to_dict(orient="records")


@app.get("/predict_trends")
async def predict_trends(limit: int = 50):
    """
    Fetch posts and predict trend scores using ML.
    """
    df = fetch_fashion_data(limit)
    trend_model.train(df)
    df = trend_model.predict(df)
    return df.to_dict(orient="records")


@app.get("/analyze_post")
async def analyze_post(query: str = Query(...)):
    """
    Analyze a single post content using Gemini AI (non-streaming).
    """
    result_text = fashion_ai.analyze(query)
    return {"status": "Done", "result": result_text}


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

