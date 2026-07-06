from typing import List, Optional


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[dict] = None,
) -> List[dict]:
    paragraphs = _split_paragraphs(text)
    merged = _merge_paragraphs(paragraphs, chunk_size)
    chunks = _create_chunks(merged, chunk_size, chunk_overlap, metadata)
    return chunks


def _split_paragraphs(text: str) -> List[str]:
    parts = text.split("\n\n")
    cleaned = []
    for part in parts:
        stripped = part.strip()
        if stripped:
            cleaned.append(stripped)
    return cleaned


def _merge_paragraphs(paragraphs: List[str], chunk_size: int) -> List[str]:
    merged = []
    current = ""
    for paragraph in paragraphs:
        if not current:
            current = paragraph
            continue
        separator = "\n\n"
        if len(current) + len(separator) + len(paragraph) <= chunk_size:
            current = current + separator + paragraph
        else:
            merged.append(current)
            current = paragraph
    if current:
        merged.append(current)
    return merged


def _create_chunks(
    merged_paragraphs: List[str],
    chunk_size: int,
    chunk_overlap: int,
    metadata: Optional[dict],
) -> List[dict]:
    chunks = []
    chunk_id = 0
    start_index = 0

    while start_index < len(merged_paragraphs):
        current_chunk = merged_paragraphs[start_index]
        end_index = start_index + 1

        while end_index < len(merged_paragraphs):
            next_para = merged_paragraphs[end_index]
            separator = "\n\n"
            if len(current_chunk) + len(separator) + len(next_para) <= chunk_size:
                current_chunk = current_chunk + separator + next_para
                end_index += 1
            else:
                break

        chunks.append({
            "text": current_chunk,
            "chunk_id": chunk_id,
            "metadata": {**(metadata or {}), "chunk_id": chunk_id},
        })

        chunk_id += 1
        if end_index >= len(merged_paragraphs):
            break

        if chunk_overlap > 0 and end_index > start_index + 1:
            start_index = end_index - 1
        else:
            start_index = end_index

    return chunks 