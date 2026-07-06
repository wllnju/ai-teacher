import os
from pathlib import Path

import fitz

from app.core.config import settings


def save_upload_file(upload_file, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "wb") as buffer:
        content = upload_file.file.read()
        buffer.write(content)
    return destination


def extract_pdf_text(path: Path) -> list[dict]:
    doc = fitz.open(path)
    pages = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append({"page_number": index, "text": text})
    return pages 