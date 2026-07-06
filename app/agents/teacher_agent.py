import re
from typing import List, Optional


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[•\-]\s*", "- ", text)
    text = re.sub(r"(?<=\w)\s(?=[.,;:!?])", "", text)
    return text.strip()


def _extract_sentences(text: str) -> List[str]:
    text = _clean_text(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if s.strip()]


def _is_summary_question(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in ["summary", "summarize", "sum up", "brief", "tl;dr", "overview"])


def _is_explanation_question(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in ["explain", "what is", "what are", "how does", "how do", "describe", "definition"])


def _word_count(text: str) -> int:
    return len(text.split())


def _truncate(text: str, max_words: int = 380) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _sort_chunks(chunks: List[dict]) -> List[dict]:
    return sorted(chunks, key=lambda c: (c.get("doc_id", ""), c.get("page_number", 0), c.get("chunk_id", "")))


def _map_section(text: str) -> Optional[str]:
    lower = text.lower()
    if any(k in lower for k in ["project vision", "vision", "goal", "objective", "purpose"]):
        return "Project vision"
    if any(k in lower for k in ["workflow", "process", "pipeline", "step", "procedure", "flow"]):
        return "Workflow"
    if any(k in lower for k in ["agent", "module", "component", "service", "system", "architecture"]):
        return "Agents"
    if any(k in lower for k in ["tech stack", "technology", "framework", "stack", "language", "database", "api"]):
        return "Tech stack"
    return None


def build_answer(question: str, chunks: List[dict]) -> tuple[str, List[str]]:
    if not chunks:
        return (
            "I could not find enough information in the uploaded documents to answer this.",
            [],
        )

    sorted_chunks = _sort_chunks(chunks)

    seen = set()
    unique_chunks = []
    for chunk in sorted_chunks:
        text = (chunk.get("text") or "").strip()
        if text and text not in seen:
            seen.add(text)
            unique_chunks.append(chunk)

    if _is_summary_question(question):
        sections = {}
        for chunk in unique_chunks:
            sentences = _extract_sentences(chunk.get("text", ""))
            for sentence in sentences:
                section = _map_section(sentence)
                if section:
                    sections.setdefault(section, [])
                    if sentence not in sections[section]:
                        sections[section].append(sentence)

        if not sections:
            sentences = _extract_sentences(" ".join(c.get("text", "") for c in unique_chunks[:3]))
            answer = " ".join(sentences[:12])
            answer = _truncate(answer)
        else:
            parts = []
            for section in ["Project vision", "Workflow", "Agents", "Tech stack"]:
                if section in sections:
                    parts.append(f"{section}:\n" + " ".join(sections[section][:4]))
            answer = "\n\n".join(parts)
            answer = _truncate(answer)

        follow_ups = [
            "Can you explain this in simpler terms?",
            "What is an example of this concept?",
            "Can you quiz me on this topic?",
        ]
        return answer, follow_ups

    if _is_explanation_question(question):
        sentences = []
        for chunk in unique_chunks[:3]:
            sentences.extend(_extract_sentences(chunk.get("text", "")))

        seen_sentences = set()
        unique_sentences = []
        for s in sentences:
            if s not in seen_sentences:
                seen_sentences.add(s)
                unique_sentences.append(s)

        answer = " ".join(unique_sentences[:12])
        answer = _truncate(answer)

        follow_ups = [
            "Can you give me a real-world example?",
            "Can you quiz me on this?",
            "What should I study next?",
        ]
        return answer, follow_ups

    sentences = []
    for chunk in unique_chunks[:4]:
        sentences.extend(_extract_sentences(chunk.get("text", "")))

    seen_sentences = set()
    unique_sentences = []
    for s in sentences:
        if s not in seen_sentences:
            seen_sentences.add(s)
            unique_sentences.append(s)

    answer = " ".join(unique_sentences[:12])
    answer = _truncate(answer, max_words=300)

    follow_ups = [
        "Can you explain this in simpler terms?",
        "What is an example of this concept?",
        "Can you quiz me on this topic?",
    ]
    return answer, follow_ups 