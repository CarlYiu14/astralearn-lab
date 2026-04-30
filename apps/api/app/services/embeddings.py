from __future__ import annotations

import hashlib

from app.core.config import settings


def _openai_enabled() -> bool:
    key = settings.openai_api_key
    return bool(key and key.strip())


def stable_placeholder_embedding(*, key: str) -> list[float]:
    """Deterministic pseudo-embedding for offline dev when no OpenAI key is set."""
    out: list[float] = []
    seed = key.encode("utf-8")
    i = 0
    while len(out) < settings.embedding_dimensions:
        seed = hashlib.sha256(seed + str(i).encode("utf-8")).digest()
        for b in seed:
            out.append((b / 255.0) * 2.0 - 1.0)
            if len(out) >= settings.embedding_dimensions:
                break
        i += 1

    norm = sum(x * x for x in out) ** 0.5
    if norm == 0:
        return out
    return [x / norm for x in out]


def _embed_openai_batch(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    vectors: list[list[float]] = []
    for item in sorted(response.data, key=lambda d: d.index):
        vec = list(item.embedding)
        if len(vec) != settings.embedding_dimensions:
            msg = f"Embedding dim mismatch: got {len(vec)}, expected {settings.embedding_dimensions}"
            raise ValueError(msg)
        vectors.append(vec)
    return vectors


def embed_texts(texts: list[str], *, stable_keys: list[str] | None = None) -> list[list[float]]:
    if not texts:
        return []

    if _openai_enabled():
        return _embed_openai_batch(texts)

    if stable_keys is None or len(stable_keys) != len(texts):
        raise ValueError("stable_keys (same length as texts) is required when OPENAI_API_KEY is not set")

    return [stable_placeholder_embedding(key=k) for k in stable_keys]
