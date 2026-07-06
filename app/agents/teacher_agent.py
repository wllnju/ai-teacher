import re
from typing import List, Optional


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?<=[a-zA-Z])\s+(?=[.,;:!?])", "", text)
    text = re.sub(r"[•\-]\s*", "- ", text)
    return text.strip()


def _extract_sentences(text: str) -> List[str]:
    text = _clean_text(text)
    if not text:
        return []
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
    trimmed = " ".join(words[:max_words])
    return trimmed.rstrip(".,;:!?") + "..."


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


def _assemble_paragraphs(
    sentences: List[str],
    max_paragraphs: int = 3,
    max_sentences_per_paragraph: int = 4,
) -> str:
    paragraphs = []
    current = []
    for sentence in sentences:
        current.append(sentence)
        if len(current) >= max_sentences_per_paragraph:
            paragraphs.append(" ".join(current))
            current = []
        if len(paragraphs) >= max_paragraphs:
            break
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


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
            for sentence in _extract_sentences(chunk.get("text", "")):
                section = _map_section(sentence)
                if section:
                    sections.setdefault(section, [])
                    if sentence not in sections[section]:
                        sections[section].append(sentence)

        if not sections:
            sentences = _extract_sentences(" ".join(c.get("text", "") for c in unique_chunks[:3]))
            answer = _assemble_paragraphs(sentences[:14], max_paragraphs=2, max_sentences_per_paragraph=5)
            answer = _truncate(answer)
        else:
            parts = []
            for section in ["Project vision", "Workflow", "Agents", "Tech stack"]:
                if section in sections:
                    sentences = sections[section][:4]
                    parts.append(section + ":\n" + _assemble_paragraphs(sentences, max_paragraphs=1, max_sentences_per_paragraph=4))
            answer = "\n\n".join(parts)
            answer = _truncate(answer)

        follow_ups = [
            "Can you explain any of these points in more detail?",
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

        answer = _assemble_paragraphs(unique_sentences[:10], max_paragraphs=2, max_sentences_per_paragraph=5)
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

    answer = _assemble_paragraphs(unique_sentences[:12], max_paragraphs=3, max_sentences_per_paragraph=4)
    answer = _truncate(answer, max_words=300)

    follow_ups = [
        "Can you explain this in simpler terms?",
        "What is an example of this concept?",
        "Can you quiz me on this topic?",
    ]
    return answer, follow_ups 