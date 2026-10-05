import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from openai import OpenAI
from pydantic import BaseModel, Field

from .memory_store import (
    init_db,
    save_memory,
    list_memories,
    search_memories,
    delete_memory,
    save_conversation,
    recent_conversations,
    create_task,
    list_tasks,
    complete_task,
    delete_task,
)

init_db()

app = FastAPI(
    title="AYRA API",
    description="AYRA Personal AI Assistant Backend",
    version="0.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    reply: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class MemoryRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    category: str = Field(default="general", max_length=100)


class TaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)


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
        "version": "0.1.1",
        "features": [
            "chat",
            "memory",
            "tasks",
            "voice",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ayra-api",
        "version": "0.1.1",
    }


@app.get("/api/status")
async def status():
    return {
        "online": True,
        "version": "0.1.1",
        "memory": True,
        "tasks": True,
        "voice": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        client = get_openai_client()

        memories = list_memories(8)
        recent = recent_conversations(8)

        memory_context = "\n".join(
            f"- [{item['category']}] {item['content']}"
            for item in memories
        )

        conversation_context = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in recent
        )

        instructions = (
            "You are AYRA, a friendly, intelligent personal AI assistant. "
            "The user is your Boss. "
            "Respond naturally in Hindi, Hinglish, or English depending on "
            "the user's language. Be helpful, warm, clear and concise.\n\n"
            "Persistent memory available to you:\n"
            f"{memory_context or '(no saved memories)'}\n\n"
            "Recent conversation:\n"
            f"{conversation_context or '(no previous conversation)'}"
        )

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=instructions,
            input=request.message,
        )

        reply = response.output_text

        save_conversation("user", request.message)
        save_conversation("ayra", reply)

        return {"reply": reply}

    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AYRA chat error: {error}",
        ) from error


@app.post("/api/speech")
async def speech(request: SpeechRequest):
    try:
        client = get_openai_client()

        audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=request.text,
            instructions=(
                "Speak as AYRA, a cute, warm, friendly female personal AI "
                "assistant. Sound natural, gentle, cheerful and conversational. "
                "Use a warm Indian-friendly English/Hinglish style when "
                "appropriate. Do not sound robotic or overly formal."
            ),
            response_format="mp3",
        )

        return Response(
            content=audio.read(),
            media_type="audio/mpeg",
        )

    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AYRA speech error: {error}",
        ) from error


@app.get("/api/memory")
async def get_memory(query: str = ""):
    if query.strip():
        return {
            "memories": search_memories(query),
            "query": query,
        }

    return {
        "memories": list_memories(),
        "query": "",
    }


@app.post("/api/memory")
async def add_memory(request: MemoryRequest):
    memory_id = save_memory(request.content, request.category)
    return {
        "success": True,
        "id": memory_id,
        "content": request.content,
        "category": request.category,
    }


@app.delete("/api/memory/{memory_id}")
async def remove_memory(memory_id: int):
    if not delete_memory(memory_id):
        raise HTTPException(status_code=404, detail="Memory not found.")

    return {"success": True}


@app.get("/api/tasks")
async def get_tasks():
    return {"tasks": list_tasks()}


@app.post("/api/tasks")
async def add_task(request: TaskRequest):
    task_id = create_task(request.title, request.description)
    return {
        "success": True,
        "id": task_id,
    }


@app.post("/api/tasks/{task_id}/complete")
async def finish_task(task_id: int):
    if not complete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found.")

    return {"success": True}


@app.delete("/api/tasks/{task_id}")
async def remove_task(task_id: int):
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found.")

    return {"success": True}
