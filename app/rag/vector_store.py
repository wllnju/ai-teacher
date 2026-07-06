from collections import Counter
from pathlib import Path
from typing import Optional, List, Dict, Any

import chromadb

from app.core.config import settings
from app.rag.embeddings import deterministic_embed_texts


class VectorStore:
    def __init__(self, persist_dir: Optional[str] = None):
        persist_dir = persist_dir or settings.chroma_persist_dir
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: List[Dict[str, Any]]) -> None:
        texts = [c["text"] for c in chunks]
        embeddings = deterministic_embed_texts(texts)

        ids = []
        for idx, chunk in enumerate(chunks):
            meta = chunk.get("metadata") or {}
            doc_id = meta.get("doc_id") or "unknown"
            page_number = meta.get("page_number") or 0
            chunk_index = meta.get("chunk_id", idx)
            chunk_id = f"{doc_id}_p{page_number}_c{chunk_index}"
            ids.append(chunk_id)

        duplicates = [chunk_id for chunk_id, count in Counter(ids).items() if count > 1]
        if duplicates:
            raise ValueError(f"Duplicate IDs detected before adding to vector store: {duplicates}")

        metadatas = [c.get("metadata", {}) for c in chunks]
        self.collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 4, doc_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        query_embeddings = deterministic_embed_texts([query_text])
        where = None
        if doc_ids:
            where = {"doc_id": {"$in": doc_ids}}
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )


vector_store = VectorStore() 