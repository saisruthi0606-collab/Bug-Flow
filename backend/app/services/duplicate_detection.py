import hashlib
import json
import math
import re
from typing import Iterable

try:
    import faiss  # type: ignore
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:
    faiss = None
    SentenceTransformer = None

_model = None
DIMENSIONS = 384

def _tokens(text: str) -> Iterable[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())

def _fallback_embedding(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in _tokens(text):
        index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % DIMENSIONS
        vector[index] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    return [value / magnitude for value in vector] if magnitude else vector

def create_embedding(text: str) -> list[float]:
    global _model
    if SentenceTransformer is not None:
        try:
            if _model is None:
                _model = SentenceTransformer("all-MiniLM-L6-v2")
            return _model.encode(text, normalize_embeddings=True).tolist()
        except Exception:
            pass
    return _fallback_embedding(text)

def serialize_embedding(embedding: list[float]) -> str:
    return json.dumps(embedding)

def deserialize_embedding(value: str | None) -> list[float] | None:
    try: return json.loads(value) if value else None
    except json.JSONDecodeError: return None

def similarity(left: list[float], right: list[float]) -> float:
    if faiss is not None:
        import numpy as np
        index = faiss.IndexFlatIP(len(left)); index.add(np.array([right], dtype="float32"))
        return max(0.0, min(1.0, float(index.search(np.array([left], dtype="float32"), 1)[0][0][0])))
    return max(0.0, min(1.0, sum(a * b for a, b in zip(left, right))))

def find_duplicates(issues, title: str, description: str | None, project_id: int | None, threshold: float = 0.58, limit: int = 5):
    target = create_embedding(f"{title} {description or ''}")
    candidates = []
    for issue in issues:
        if project_id is not None and issue.project_id != project_id:
            continue
        existing = deserialize_embedding(getattr(issue, 'embedding', None)) or create_embedding(f"{issue.title} {issue.description or ''}")
        score = similarity(target, existing)
        if score >= threshold:
            candidates.append({"id": issue.id, "title": issue.title, "similarity": round(score * 100, 1)})
    return sorted(candidates, key=lambda row: row["similarity"], reverse=True)[:limit], target
