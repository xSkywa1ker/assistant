from __future__ import annotations

from jarvis.backend.app.memory.store import cosine_similarity, simple_sentence_embedding


def test_simple_sentence_embedding_normalizes():
    vector = simple_sentence_embedding("Jarvis helps helps")
    assert abs(sum(vector) - 1.0) < 1e-6


def test_cosine_similarity_basic():
    a = [1.0, 0.0]
    b = [1.0, 0.0]
    assert cosine_similarity(a, b) == 1.0
