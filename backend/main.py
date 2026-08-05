from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from langchain_core.messages import HumanMessage

from graph import build_graph, TokenUsageCallbackHandler
from fastapi.middleware.cors import CORSMiddleware

# ---------------- APP ---------------- #

app = FastAPI(
    title="Weather Multi-Agent API",
    description="LangGraph tabanlı multi-agent hava durumu uygulaması",
    version="1.0.0",
)

print("CORS AKTIF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Graph uygulama başlarken oluşturulur
graph = build_graph()


# ---------------- REQUEST / RESPONSE ---------------- #

class ChatRequest(BaseModel):
    message: str
    current_user: Optional[str] = None
    session_id: str


class ChatResponse(BaseModel):
    response: str
    current_user: Optional[str] = None
    input_tokens: int
    output_tokens: int
    total_tokens: int


# ---------------- HEALTH ---------------- #

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# ---------------- CHAT ---------------- #

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    token_tracker = TokenUsageCallbackHandler()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
            ],
            "current_user": request.current_user,
        },
        config={
            "configurable": {
                "thread_id": request.session_id
            },
            "callbacks": [token_tracker]
        },
    )

    # Graph'ın son mesajını al
    last_message = result["messages"][-1]

    response_text = last_message.content

    return ChatResponse(
        response=response_text,
        current_user=result.get("current_user"),
        input_tokens=token_tracker.input_tokens,
        output_tokens=token_tracker.output_tokens,
        total_tokens=token_tracker.total_tokens,
    )