import numpy as np

from services import embeddings


def _chunks(text: str) -> list[str]:
    parts = [line.strip() for line in text.replace("\r", "").split("\n") if line.strip()]
    return parts or [text.strip()]


def add(session: dict, text: str) -> int:
    chunks = _chunks(text)
    vectors = embeddings.embed(chunks)
    store = session.setdefault("notes", [])
    for chunk, vector in zip(chunks, vectors):
        store.append({"text": chunk, "vector": vector})
    return len(chunks)


def count(session: dict) -> int:
    return len(session.get("notes", []))


def clear(session: dict) -> None:
    session["notes"] = []


def retrieve(session: dict, query: str | None, k: int = 4) -> list[str]:
    store = session.get("notes")
    if not store:
        return []
    if not query:
        return [item["text"] for item in store[:k]]
    query_vector = embeddings.embed([query])[0]
    ranked = sorted(store, key=lambda item: float(np.dot(query_vector, item["vector"])), reverse=True)
    return [item["text"] for item in ranked[:k]]
