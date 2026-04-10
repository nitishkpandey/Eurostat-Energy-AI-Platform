from __future__ import annotations

from typing import Any

from backend.services.ai.chatbot import answer_question


def ask_question(question: str) -> dict[str, Any]:
    return answer_question(question)
