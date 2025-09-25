import os, asyncio, json
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_API_KEY
)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=gemini_client)
instructions = "You are a fashion trend expert. Analyze content from social media, blogs, or search results to identify emerging fashion trends. Provide a concise, professional summary highlighting key patterns, colors, styles, and consumer preferences."
fashion_agent = Agent(name="Gemini Fashion Agent", instructions=instructions, model=gemini_model)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/search")
async def search_stream(query: str = Query(...)):
    async def event_stream():
        yield f"data: {json.dumps({'status': 'Thinking...'})}\n\n"
        await asyncio.sleep(0.5)
        result = Runner.run_streamed(fashion_agent, input=query)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield f"data: {json.dumps({'status': 'Streaming', 'delta': event.data.delta})}\n\n"
        yield f"data: {json.dumps({'status': 'Done'})}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
