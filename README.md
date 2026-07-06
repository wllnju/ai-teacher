# AI Teacher

An AI-powered teacher platform that teaches from uploaded documents using a RAG pipeline, with live voice interaction support and specialized AI agents for tutoring.

## Features

- Teach from uploaded documents via RAG
- Live voice interaction via WebSocket
- Student interruptions during teacher speech
- Specialized AI agents:
  - Main teacher
  - Quiz generation
  - Examples
  - Diagrams
  - Summaries
  - Resource recommendation
  - Progress tracking

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

## Upload a document

```bash
curl -X POST "http://localhost:8000/api/v1/upload" -F "file=@/path/to/notes.pdf"
```

List uploaded documents:

```bash
curl "http://localhost:8000/api/v1/documents"
```

Health check:

```bash
curl "http://localhost:8000/health"
```