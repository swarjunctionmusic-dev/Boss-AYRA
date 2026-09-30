import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from openai import OpenAI
from pydantic import BaseModel


app = FastAPI(
    title="AYRA API",
    description="AYRA Personal AI Assistant Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class SpeechRequest(BaseModel):
    text: str


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=api_key)


@app.get("/")
async def root():
    return {
        "name": "AYRA",
        "status": "online",
        "message": "AYRA backend is running.",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ayra-api",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "You are AYRA, a friendly, intelligent personal AI assistant. "
            "The user is your Boss. "
            "Respond naturally in Hindi, Hinglish, or English depending on the user. "
            "Be helpful, warm, clear, and concise."
        ),
        input=request.message,
    )

    return {
        "reply": response.output_text
    }


@app.post("/api/speech")
async def speech(request: SpeechRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required.")

    client = get_openai_client()

    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=request.text,
        instructions=(
            "Speak as AYRA, a cute, warm, friendly female personal AI assistant. "
            "Sound natural, gentle, cheerful, and conversational. "
            "Use a warm Indian-friendly English/Hinglish style when appropriate. "
            "Do not sound robotic or overly formal."
        ),
        response_format="mp3",
    )

    return Response(
        content=audio.read(),
        media_type="audio/mpeg",
    )