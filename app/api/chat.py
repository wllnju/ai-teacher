from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from app.rag.retriever import retrieve
from app.agents.teacher_agent import build_answer


router = APIRouter()


class ChatRequest(BaseModel):
    student_id: str
    doc_ids: list[str]
    question: str
    student_level: str = "beginner"
    top_k: int = 5


class Citation(BaseModel):
    doc_id: str
    filename: str
    page_number: int
    chunk_id: str


class RetrievedChunk(BaseModel):
    doc_id: str
    filename: str
    page_number: int
    chunk_id: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    agent: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    suggested_follow_up: list[str]


def build_answer(question: str, chunks: list[dict]) -> tuple[str, list[str]]:
    raise RuntimeError("Use app.agents.teacher_agent.build_answer instead.")


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    top_k = max(1, request.top_k)
    chunks = retrieve(request.question, request.doc_ids, top_k=top_k)

    answer, follow_ups = build_answer(request.question, chunks)

    citations = []
    retrieved = []
    for chunk in chunks:
        citations.append(Citation(
            doc_id=chunk["doc_id"],
            filename=chunk["filename"],
            page_number=chunk["page_number"],
            chunk_id=chunk["chunk_id"],
        ))
        retrieved.append(RetrievedChunk(
            doc_id=chunk["doc_id"],
            filename=chunk["filename"],
            page_number=chunk["page_number"],
            chunk_id=chunk["chunk_id"],
            text=chunk["text"],
        ))

    return ChatResponse(
        answer=answer,
        agent="teacher",
        citations=citations,
        retrieved_chunks=retrieved,
        suggested_follow_up=follow_ups,
    ) 