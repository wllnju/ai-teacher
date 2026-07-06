import unittest

from app.agents.diagram_agent import build_diagram


def _chunk(doc_id="1", filename="a.pdf", page_number=1, chunk_id="1", text="Test text."):
    return {
        "doc_id": doc_id,
        "filename": filename,
        "page_number": page_number,
        "chunk_id": chunk_id,
        "text": text,
        "distance": 0.1,
    }


class TestDiagramAgent(unittest.TestCase):
    def test_flowchart_request(self):
        chunks = [_chunk(text="The workflow has upload, indexing, and retrieval steps.")]
        result = build_diagram("What is the workflow?", chunks, diagram_type="flowchart")
        self.assertEqual(result["agent"], "diagram")
        self.assertEqual(result["diagram_type"], "flowchart")
        self.assertTrue(result["mermaid"].startswith("flowchart TD"))
        self.assertTrue(len(result["citations"]) > 0)
        self.assertTrue(len(result["retrieved_chunks"]) > 0)

    def test_sequence_request(self):
        chunks = [_chunk(text="The user uploads a PDF, then the teacher responds with an answer.")]
        result = build_diagram("Show me the voice interaction sequence.", chunks, diagram_type="sequence")
        self.assertEqual(result["agent"], "diagram")
        self.assertEqual(result["diagram_type"], "sequence")
        self.assertTrue(result["mermaid"].startswith("sequenceDiagram"))
        self.assertTrue(len(result["citations"]) > 0)

    def test_architecture_request(self):
        chunks = [_chunk(text="The backend exposes FastAPI endpoints. The frontend is a web app.")]
        result = build_diagram("Describe the system architecture.", chunks, diagram_type="architecture")
        self.assertEqual(result["agent"], "diagram")
        self.assertEqual(result["diagram_type"], "architecture")
        self.assertTrue(result["mermaid"].startswith("graph TD"))
        self.assertTrue(len(result["citations"]) > 0)

    def test_concept_map_request(self):
        chunks = [_chunk(text="RAG combines retrieval and generation for grounded answers.")]
        result = build_diagram("Explain RAG.", chunks, diagram_type="concept_map")
        self.assertEqual(result["agent"], "diagram")
        self.assertEqual(result["diagram_type"], "concept_map")
        self.assertTrue(result["mermaid"].startswith("mindmap"))
        self.assertTrue(len(result["citations"]) > 0)

    def test_empty_retrieval_insufficient_context(self):
        result = build_diagram("What is the project vision?", [])
        self.assertEqual(result["agent"], "diagram")
        self.assertEqual(result["mermaid"], "")
        self.assertEqual(result["explanation"], "insufficient_context")
        self.assertEqual(result["citations"], [])
        self.assertEqual(result["retrieved_chunks"], [])
        self.assertEqual(result["suggested_follow_up"], [])


if __name__ == "__main__":
    unittest.main()
