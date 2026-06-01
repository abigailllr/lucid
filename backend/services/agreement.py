import numpy as np

from services import embeddings


def consensus(texts: list[str]) -> tuple[int, float]:
    if len(texts) == 1:
        return 0, 1.0
    vectors = embeddings.embed(texts)
    similarity = vectors @ vectors.T
    medoid = int(np.argmax(similarity.sum(axis=1)))
    n = len(texts)
    off_diagonal = (similarity.sum() - n) / (n * n - n)
    return medoid, float(off_diagonal)
