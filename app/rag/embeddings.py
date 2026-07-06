import hashlib
from typing import List


def deterministic_embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(min(128, len(digest))):
            vector.append(digest[i] / 255.0)
        embeddings.append(vector)
    return embeddings 