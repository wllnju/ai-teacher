import re
from typing import List, Optional, Dict, Any


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?<=[a-zA-Z])\s+(?=[.,;:!?])", "", text)
    text = re.sub(r"[•\-]\s*", "- ", text)
    return text.strip()


def _extract_sentences(text: str) -> List[str]:
    text = _clean(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if s.strip()]


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _truncate(text: str, max_words: int = 300) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _infer_diagram_type(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ["workflow", "process", "steps", "flow", "pipeline"]):
        return "flowchart"
    if any(k in q for k in ["interaction", "sequence", "voice", "interrupt", "timing"]):
        return "sequence"
    if any(k in q for k in ["architecture", "system", "components", "backend", "frontend", "structure"]):
        return "architecture"
    return "concept_map"


def _build_flowchart(sentences: List[str], title: str) -> str:
    lines = ["flowchart TD"]
    nodes = []
    for idx, sent in enumerate(sentences[:6]):
        label = _clean(sent).replace('"', "'")
        if len(label) > 80:
            label = " ".join(label.split()[:12]) + "..."
        node_id = f"N{idx}"
        nodes.append(node_id)
        lines.append(f'    {node_id}["{label}"]')
    for idx in range(len(nodes) - 1):
        lines.append(f"    {nodes[idx]} --> {nodes[idx + 1]}")
    if len(nodes) == 1:
        lines.append(f'    T["{title}"]')
        lines.append(f"    T --> {nodes[0]}")
    return "\n".join(lines)


def _build_sequence(sentences: List[str], title: str) -> str:
    actor_keywords = {
        "user": "User",
        "student": "Student",
        "teacher": "Teacher",
        "ai": "AI Teacher",
        "voice": "Voice",
        "system": "System",
        "database": "Database",
        "db": "Database",
        "frontend": "Frontend",
        "backend": "Backend",
    }

    participants = {}
    messages = []

    def ensure(name: str) -> str:
        if name not in participants:
            aid = f"A{len(participants) + 1}"
            participants[name] = aid
        return participants[name]

    for name in ["User", "AI Teacher", "System"]:
        ensure(name)

    for sent in sentences[:5]:
        current_actor = None
        for keyword, name in actor_keywords.items():
            if keyword in sent.lower():
                current_actor = name
                break
        if current_actor is None:
            current_actor = "User"

        actor_id = ensure(current_actor)
        label = sent.replace('"', "'")
        if len(label) > 80:
            label = " ".join(label.split()[:14]) + "..."

        other_candidates = [n for n in participants if n != current_actor]
        if not other_candidates:
            other_candidates = ["System"]
        target = other_candidates[0]
        target_id = participants[target]
        messages.append(f"    {actor_id}->>{target_id}: {label}")

    lines = ["sequenceDiagram"]
    for name, aid in participants.items():
        lines.append(f"    participant {aid} as {name}")
    lines.extend(messages)
    return "\n".join(lines)


def _build_architecture(sentences: List[str], title: str) -> str:
    lines = ["graph TD"]
    nodes = []
    keywords = [
        "frontend",
        "backend",
        "api",
        "database",
        "vector",
        "rag",
        "agent",
        "module",
        "service",
        "voice",
        "upload",
        "retriever",
        "embeddings",
        "teacher",
        "student",
        "chroma",
        "pdf",
    ]
    for idx, sent in enumerate(sentences[:6]):
        label = _clean(sent).replace('"', "'")
        if len(label) > 80:
            label = " ".join(label.split()[:12]) + "..."
        node_id = f"C{idx}"
        nodes.append(node_id)
        lines.append(f'    {node_id}["{label}"]')
        style = []
        for kw in keywords:
            if kw in label.lower():
                style.append(f"fill:#f9f,stroke:#333,stroke-width:1px")
                break
        if style:
            lines.append(f"    style {node_id} {style[0]}")
    for idx in range(len(nodes) - 1):
        lines.append(f"    {nodes[idx]} --> {nodes[idx + 1]}")
    if len(nodes) == 1:
        lines.append(f'    T["{title}"]')
        lines.append(f"    T --> {nodes[0]}")
    return "\n".join(lines)


def _build_concept_map(sentences: List[str], title: str) -> str:
    lines = ["mindmap"]
    safe_title = _clean(title).replace('"', "'")
    lines.append(f"  root(({safe_title}))")
    for sent in sentences[:8]:
        label = _clean(sent).replace('"', "'")
        words = label.split()
        if len(words) > 8:
            label = " ".join(words[:8]) + "..."
        lines.append(f"  {label}")
    return "\n".join(lines)


def build_diagram(question: str, chunks: List[dict], diagram_type: Optional[str] = None) -> Dict[str, Any]:
    if not chunks:
        return {
            "agent": "diagram",
            "diagram_type": diagram_type or _infer_diagram_type(question),
            "title": question.strip() or "Diagram",
            "mermaid": "",
            "explanation": "insufficient_context",
            "citations": [],
            "retrieved_chunks": [],
            "suggested_follow_up": [],
        }

    diagram_type = diagram_type or _infer_diagram_type(question)
    texts = [c.get("text", "") for c in chunks if c.get("text")]
    combined = " ".join(texts)
    sentences = _dedupe(_extract_sentences(combined))
    if not sentences:
        sentences = [s.strip() for s in combined.split(". ") if s.strip()]

    title = " ".join(question.split()[:6])
    if not title.endswith("?") and not title.endswith("."):
        title += "?"

    explanation = f"A {diagram_type} grounded in {len(chunks)} retrieved chunk(s)."

    if diagram_type == "flowchart":
        mermaid = _build_flowchart(sentences, title)
    elif diagram_type == "sequence":
        mermaid = _build_sequence(sentences, title)
    elif diagram_type == "architecture":
        mermaid = _build_architecture(sentences, title)
    else:
        mermaid = _build_concept_map(sentences, title)

    seen = set()
    citations = []
    retrieved = []
    for chunk in chunks:
        text = (chunk.get("text") or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        citations.append({
            "doc_id": chunk.get("doc_id", "unknown"),
            "filename": chunk.get("filename", ""),
            "page_number": chunk.get("page_number", 0),
            "chunk_id": chunk.get("chunk_id", ""),
        })
        retrieved.append({
            "doc_id": chunk.get("doc_id", "unknown"),
            "filename": chunk.get("filename", ""),
            "page_number": chunk.get("page_number", 0),
            "chunk_id": chunk.get("chunk_id", ""),
            "text": chunk.get("text", ""),
        })

    return {
        "agent": "diagram",
        "diagram_type": diagram_type,
        "title": title,
        "mermaid": mermaid,
        "explanation": explanation,
        "citations": citations,
        "retrieved_chunks": retrieved,
        "suggested_follow_up": [
            "Can you explain one part in more detail?",
            "Can you show the next stage?",
            "Can you quiz me on this flow?"
        ],
    } 