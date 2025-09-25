from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
from starlette.concurrency import run_in_threadpool

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")
if not google_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables!")

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search_fashion(req: SearchRequest):
    # Step 1: Primary agent - detailed fashion prediction
    primary_messages = [
        {"role": "system", "content": "You are a fashion trend prediction assistant."},
        {"role": "user", "content": req.query}
    ]

    def call_primary_agent():
        return gemini.chat.completions.create(
            model="gemini-2.5-flash",
            messages=primary_messages,
            max_tokens=300,
            temperature=0.7
        )

    primary_response = await run_in_threadpool(call_primary_agent)
    primary_answer = primary_response.choices[0].message.content

    # Step 2: Refinement agent - make it concise
    refine_messages = [
        {"role": "system", "content": "You are a summarization assistant. Make the response concise and clear."},
        {"role": "user", "content": primary_answer}
    ]

    def call_refine_agent():
        return gemini.chat.completions.create(
            model="gemini-2.5-flash",
            messages=refine_messages,
            max_tokens=150,
            temperature=0.5
        )

    refined_response = await run_in_threadpool(call_refine_agent)
    concise_answer = refined_response.choices[0].message.content

    return {"result": concise_answer}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
