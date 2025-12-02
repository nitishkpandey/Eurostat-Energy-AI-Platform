from __future__ import annotations

from typing import Dict

from .build_knowledge_base import build_insights_df
from .rag_engine import semantic_search


def _fastest_rising_gep_answer() -> str:
    """
    Special intent handler for:
    'Which country's GEP is rising fastest?'
    """
    df = build_insights_df()

    if df.empty:
        return "I couldn't find any processed GEP data. Please run the ETL pipeline first."

    # Filter rows where indicator is GEP
    gep_mask = df["indicator"].isin(["nrg_cb_e", "GEP"])
    sub = df[gep_mask].copy()

    if sub.empty:
        return "I couldn't find Gross Electricity Production (GEP) in the dataset."

    # Highest slope = fastest rising
    sub = sub.sort_values("slope_per_year", ascending=False)
    top = sub.iloc[0]

    country = top["geo"]
    ind_name = top["indicator_name"]
    slope = top["slope_per_year"]
    start_y = int(top["start_year"])
    end_y = int(top["end_year"])
    start_v = top["start_value"]
    end_v = top["end_value"]

    answer = (
        f"Based on the available data, **{country}** has the fastest rising "
        f"**{ind_name}** trend.\n\n"
        f"- Period: {start_y} → {end_y}\n"
        f"- Values: {start_v:.2f} → {end_v:.2f}\n"
        f"- Average increase: {slope:.2f} units per year\n"
    )

    return answer


def answer_question(question: str) -> Dict[str, str]:
    """
    Main entrypoint used by Streamlit.

    It detects special intent-based questions first,
    then falls back to semantic similarity.
    """
    if not question or not question.strip():
        return {
            "answer": "Please ask a question about countries, indicators, or trends.",
            "mode": "none",
        }

    q = question.lower().strip()

    # Intent-based handler (faster + exact)
    if (
        ("rising" in q or "increasing" in q or "growing" in q)
        and ("gep" in q or "gross electricity" in q)
    ):
        return {
            "answer": _fastest_rising_gep_answer(),
            "mode": "intent",
        }

    # Default = semantic similarity search (RAG)
    semantic_answer = semantic_search(question)

    return {
        "answer": semantic_answer,
        "mode": "semantic",
    }