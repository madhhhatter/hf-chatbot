import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

client = InferenceClient(
    provider="featherless-ai",
    api_key=HF_TOKEN,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def generate_reply(user_message: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=200,
    )
    return completion.choices[0].message.content

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(request.message)
    return ChatResponse(reply=reply)

@app.get("/health")
def health_check():
    return {"status": "ok"}