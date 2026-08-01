"""End-to-end RAG pipeline for chatbot queries."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from src.config import get_secret

from src.analysis.validators import validate_chat_answer
from src.rag.fallback_answer import build_retrieval_answer
from src.rag.gate import (
    OUT_OF_SCOPE_MESSAGE,
    REFUSAL_MESSAGE,
    is_out_of_scope,
    max_similarity,
    passes_threshold,
)
from src.rag.generator import generate_answer
from src.rag.retriever import RetrievedReview, ReviewRetriever


@dataclass
class ChatResult:
    question: str
    answer: str
    retrieved: list[RetrievedReview] = field(default_factory=list)
    refused: bool = False
    groq_called: bool = False
    validation_ok: bool = True
    validation_errors: list[str] = field(default_factory=list)
    max_similarity: float = 0.0
    meta: dict = field(default_factory=dict)


def _fallback_enabled() -> bool:
    return os.getenv("RAG_FALLBACK", "true").lower() in ("1", "true", "yes")


def _use_groq() -> bool:
    return os.getenv("RAG_USE_GROQ", "true").lower() in ("1", "true", "yes")


def _finish_with_fallback(
    question: str,
    retrieved: list[RetrievedReview],
    sim: float,
    reason: str,
) -> ChatResult:
    answer = build_retrieval_answer(question, retrieved)
    allowed_ids = {r.review_id for r in retrieved}
    validation = validate_chat_answer(answer, allowed_ids)
    return ChatResult(
        question=question,
        answer=answer,
        retrieved=retrieved,
        refused=False,
        groq_called=False,
        validation_ok=validation.ok,
        validation_errors=validation.errors,
        max_similarity=sim,
        meta={"fallback": True, "fallback_reason": reason},
    )


def answer_question(
    question: str,
    retriever: ReviewRetriever,
    threshold: float | None = None,
) -> ChatResult:
    question = question.strip()
    if not question:
        return ChatResult(
            question=question,
            answer="Please enter a question about Zepto review themes or user behavior.",
            refused=True,
        )

    if is_out_of_scope(question):
        retrieved = retriever.retrieve(question)
        return ChatResult(
            question=question,
            answer=OUT_OF_SCOPE_MESSAGE,
            retrieved=retrieved,
            refused=True,
            groq_called=False,
            max_similarity=max_similarity(retrieved),
        )

    retrieved = retriever.retrieve(question)
    sim = max_similarity(retrieved)

    if not passes_threshold(retrieved, threshold):
        if _fallback_enabled() and retrieved:
            return _finish_with_fallback(question, retrieved, sim, "below_similarity_threshold")
        return ChatResult(
            question=question,
            answer=REFUSAL_MESSAGE,
            retrieved=retrieved,
            refused=True,
            groq_called=False,
            max_similarity=sim,
        )

    if not _use_groq() or not get_secret("GROQ_API_KEY"):
        return _finish_with_fallback(question, retrieved, sim, "groq_disabled_or_missing_key")

    allowed_ids = {r.review_id for r in retrieved}
    try:
        answer, meta = generate_answer(question, retrieved)
    except Exception as exc:
        reason = type(exc).__name__
        if _fallback_enabled():
            return _finish_with_fallback(question, retrieved, sim, f"groq_error_{reason}")
        return ChatResult(
            question=question,
            answer=f"Error generating answer: {exc}. Showing retrieved reviews instead.",
            retrieved=retrieved,
            refused=True,
            groq_called=False,
            max_similarity=sim,
        )

    validation = validate_chat_answer(answer, allowed_ids)
    if not validation.ok:
        if _fallback_enabled():
            return _finish_with_fallback(question, retrieved, sim, "validation_failed")
        return ChatResult(
            question=question,
            answer="Answer failed validation. See source excerpts below.",
            retrieved=retrieved,
            refused=True,
            groq_called=True,
            validation_ok=False,
            validation_errors=validation.errors,
            max_similarity=sim,
            meta=meta,
        )

    return ChatResult(
        question=question,
        answer=answer,
        retrieved=retrieved,
        refused=False,
        groq_called=True,
        validation_ok=True,
        max_similarity=sim,
        meta=meta,
    )
