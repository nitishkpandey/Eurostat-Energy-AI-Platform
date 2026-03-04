"""Insights router – AI-powered question answering over energy data."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.schemas import InsightResponse
from llm_app.chatbot import answer_question

router = APIRouter(prefix="/insights", tags=["insights"])


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask", response_model=InsightResponse)
def ask_insight(body: QuestionRequest) -> InsightResponse:
    """Answer a natural-language question about European energy data."""
    if not body.question or not body.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    result = answer_question(body.question)
    return InsightResponse(answer=result["answer"], mode=result.get("mode", "semantic"))
