from typing import List, Optional

from app.rag.embeddings import deterministic_embed_texts
from app.rag.vector_store import vector_store


def retrieve(query: str, doc_ids: Optional[List[str]], top_k: int = 4) -> List[dict]:
    result = vector_store.query(query, top_k=top_k, doc_ids=doc_ids)
    chunks: List[dict] = []

    if not result or "ids" not in result or not result["ids"]:
        return chunks

    ids = result["ids"][0] if result.get("ids") else []
    documents = result.get("documents", [[]])
    documents = documents[0] if documents else []
    metadatas = result.get("metadatas", [[]])
    metadatas = metadatas[0] if metadatas else []
    distances = result.get("distances", [[]])
    distances = distances[0] if distances else []

    for idx, chroma_id in enumerate(ids):
        text = documents[idx] if idx < len(documents) else ""
        meta = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None

        chunk = {
            "doc_id": meta.get("doc_id", "unknown"),
            "filename": meta.get("filename", ""),
            "page_number": meta.get("page_number", 0),
            "chunk_id": chroma_id,
            "text": text,
            "distance": distance,
        }
        chunks.append(chunk)

    return chunks 