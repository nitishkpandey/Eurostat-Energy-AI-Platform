from __future__ import annotations

import os
import warnings
from functools import lru_cache
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

from sentence_transformers import SentenceTransformer

from .build_knowledge_base import build_insights_df


@lru_cache(maxsize=1)
def get_index() -> Tuple[pd.DataFrame, SentenceTransformer, np.ndarray]:
    """
    Build & cache:
      - insights_df
      - SentenceTransformer model
      - Embedding matrix
    """
    df = build_insights_df()

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            module="huggingface_hub.file_download",
        )
        model = SentenceTransformer("all-MiniLM-L6-v2")

    if df.empty:
        X = np.zeros((0, model.get_sentence_embedding_dimension()))
        return df, model, X

    # Create embeddings for the insights
    X = model.encode(df["insight_text"].tolist(), show_progress_bar=False)
    
    return df, model, X


def semantic_search(question: str, top_k: int = 5) -> str:
    """
    Return a human-readable answer based purely on
    semantic similarity between the question and the
    precomputed insights using vector embeddings.
    """
    df, model, X = get_index()

    if df.empty or X.shape[0] == 0:
        return "I don't have enough processed data yet. Please run the ETL pipeline first."

    # Encode the user's question
    q_vec = model.encode([question], show_progress_bar=False)
    
    # Calculate cosine similarity between question and all insights
    sims = cosine_similarity(q_vec, X)[0]
    
    # Get top_k most similar insights
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
        + "\n\n(This is based on semantic vector similarity over precomputed country–indicator insights.)"
    )
    return answer
