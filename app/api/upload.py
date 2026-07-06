import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.rag.loaders import extract_pdf_text, save_upload_file
from app.rag.chunker import chunk_text
from app.rag.vector_store import vector_store


router = APIRouter()


def load_documents() -> dict:
    p = Path(settings.documents_json)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_documents(data: dict) -> None:
    p = Path(settings.documents_json)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@router.post("/upload", tags=["Upload"])
async def upload_document(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported in this version.")

    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    dest = uploads_dir / file.filename

    save_upload_file(file, dest)

    pages = extract_pdf_text(dest)
    doc_id = str(uuid.uuid4())
    all_chunks = []

    documents = load_documents()
    documents[doc_id] = {
        "doc_id": doc_id,
        "filename": file.filename,
        "created_at": datetime.utcnow().isoformat(),
        "page_count": len(pages),
        "chunk_count": 0,
    }
    save_documents(documents)

    for page in pages:
        metadata = {"doc_id": doc_id, "filename": file.filename, "page_number": page["page_number"]}
        chunks = chunk_text(page["text"], metadata=metadata)
        for c in chunks:
            all_chunks.append(c)

    if all_chunks:
        vector_store.add(all_chunks)
        documents[doc_id]["chunk_count"] = len(all_chunks)
        save_documents(documents)

    return JSONResponse({
        "doc_id": doc_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(all_chunks),
        "status": "indexed",
    }) 