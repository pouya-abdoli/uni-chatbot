from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from agent import ask

app = FastAPI()

# Allow the Vite dev server (frontend) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request body for /chat."""

    message: str  # the user's new message
    history: list[dict] = []  # prior messages: [{"role": ..., "content": ...}, ...]


@app.post("/chat")
def chat(req: ChatRequest):
    """Stream the AI reply to the client chunk by chunk (plain text)."""

    # StreamingResponse forwards each piece to the client immediately
    return StreamingResponse(
        ask(req.message, req.history),
        media_type="text/plain; charset=utf-8",
    )
