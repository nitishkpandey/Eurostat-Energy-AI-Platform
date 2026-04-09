from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from backend.core.database import load_observations_df


OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_current_figure(file_name: str) -> None:
    file_path = OUTPUT_DIR / file_name
    plt.tight_layout()
    plt.savefig(file_path)
    print(f"Saved plot: {file_path}")
    plt.close()


def plot_country_trend(df: pd.DataFrame, country_code: str, indicator_code: str) -> None:
    subset = df[(df["country_code"] == country_code) & (df["indicator_code"] == indicator_code)]
    subset = subset.sort_values(by="time")

    if subset.empty:
        print(f"No data for {country_code} and {indicator_code}")
        return

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=subset, x="time", y="value", marker="o")
    plt.title(f"{indicator_code} Trend for {country_code}")
    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.xticks(rotation=45)
    plt.grid(True)
    _save_current_figure(f"{country_code}_{indicator_code}_trend.png")


def plot_top_countries(df: pd.DataFrame, indicator_code: str) -> None:
    subset = df[df["indicator_code"] == indicator_code]
    if subset.empty:
        print(f"No data for indicator: {indicator_code}")
        return

    latest_year = int(subset["year"].max())
    latest_subset = subset[subset["year"] == latest_year]

    top = latest_subset.groupby("country_code")["value"].sum().nlargest(10).reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x="value", y="country_code")
    plt.title(f"Top 10 Countries by {indicator_code} in {latest_year}")
    plt.xlabel("Value")
    plt.ylabel("Country")
    plt.grid(True)
    _save_current_figure(f"top_10_{indicator_code}_{latest_year}.png")


def plot_heatmap(df: pd.DataFrame, indicator_code: str) -> None:
    subset = df[df["indicator_code"] == indicator_code]
    if subset.empty:
        print(f"No data for indicator: {indicator_code}")
        return

    pivot = subset.pivot_table(index="country_code", columns="year", values="value", aggfunc="sum")

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, cmap="viridis", linewidths=0.5, linecolor="gray")
    plt.title(f"Heatmap of {indicator_code} Over Time")
    plt.xlabel("Year")
    plt.ylabel("Country")
    _save_current_figure(f"heatmap_{indicator_code}.png")


def generate_all() -> None:
    df = load_observations_df()
    if df.empty:
        print("No observations found. Run ETL before generating visualizations.")
        return

    print(f"Loaded {len(df)} records from PostgreSQL.")
    plot_country_trend(df, "DE", "GEP")
    plot_top_countries(df, "GEP")
    plot_heatmap(df, "GEP")


if __name__ == "__main__":
    generate_all()