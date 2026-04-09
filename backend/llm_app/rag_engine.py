from __future__ import annotations

from functools import lru_cache
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .build_knowledge_base import build_insights_df


@lru_cache(maxsize=1)
def get_index() -> Tuple[pd.DataFrame, TfidfVectorizer, np.ndarray]:
    """
    Build & cache:
      - insights_df
      - TF-IDF vectorizer
      - TF-IDF matrix
    """
    df = build_insights_df()

    if df.empty:
        vectorizer = TfidfVectorizer()
        X = np.zeros((0, 1))
        return df, vectorizer, X

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
    )
    X = vectorizer.fit_transform(df["insight_text"])
    return df, vectorizer, X


def semantic_search(question: str, top_k: int = 5) -> str:
    """
    Return a human-readable answer based purely on
    semantic similarity between the question and the
    precomputed insights.
    """
    df, vectorizer, X = get_index()

    if df.empty or X.shape[0] == 0:
        return "I don't have enough processed data yet. Please run the ETL pipeline first."

    q_vec = vectorizer.transform([question])
    sims = cosine_similarity(q_vec, X)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]

    relevant = df.iloc[top_idx].copy()
    relevant["similarity"] = sims[top_idx]

    lines = []
    for _, row in relevant.iterrows():
        country = row["geo"]
        indicator = row["indicator_name"]
        trend = row["trend_label"]
        start_y, end_y = int(row["start_year"]), int(row["end_year"])
        start_v, end_v = row["start_value"], row["end_value"]

        lines.append(
            f"- {country}, {indicator}: {start_v:.2f} → {end_v:.2f} "
            f"({start_y}–{end_y}), trend: **{trend}**"
        )

    answer = (
        "Here are the most relevant trends I found:\n\n"
        + "\n".join(lines)
        + "\n\n(This is based on semantic similarity over precomputed country–indicator insights.)"
    )
    return answer