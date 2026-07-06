from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from app.rag.retriever import retrieve
from app.agents.diagram_agent import build_diagram


router = APIRouter()


class DiagramRequest(BaseModel):
    student_id: str
    doc_ids: list[str]
    topic: str = ""
    question: str
    student_level: str = "beginner"
    diagram_type: str = ""
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


class DiagramResponse(BaseModel):
    agent: str
    diagram_type: str
    title: str
    mermaid: str
    explanation: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    suggested_follow_up: list[str]


@router.post("/diagram", response_model=DiagramResponse, tags=["Diagram"])
async def create_diagram(request: DiagramRequest) -> DiagramResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    chunks = retrieve(request.question, request.doc_ids, top_k=5)
    result = build_diagram(request.question, chunks, request.diagram_type or None)

    return DiagramResponse(
        agent=result["agent"],
        diagram_type=result["diagram_type"],
        title=result["title"],
        mermaid=result["mermaid"],
        explanation=result["explanation"],
        citations=[Citation(**c) for c in result["citations"]],
        retrieved_chunks=[RetrievedChunk(**c) for c in result["retrieved_chunks"]],
        suggested_follow_up=result["suggested_follow_up"],
    ) 