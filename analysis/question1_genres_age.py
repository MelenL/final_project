"""
Question 1: What are the main musical genres of the last year?

This revised script removes every age-based analysis because the scraped user
file does not contain valid age information. It also avoids user-level genre
plots because `users.csv` does not provide usable `top_genres` values in the
current dataset.

To still answer the core question about the main musical genres, the analysis
now relies on the data that is actually available:
  - genre metadata from `genres.csv` (used as a genre vocabulary)
  - artist popularity and tag metadata from `artists.csv`
  - user scrobble metadata only for a short data-quality check (no age plots)

This script analyzes:
  - The main genres represented in the scraped artist sample
  - Genre popularity by total listeners
  - Genre popularity by total play count
  - Whether some genres generate deeper engagement than others
  - Artist-level loyalty distributions across genres

Outputs: Multiple plots saved to analysis/plots/
"""

from __future__ import annotations

import os
from typing import Dict, Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# -----------------------------------------------------------------------------
# Loading
# -----------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the CSV files used by the analysis."""
    genres_df = pd.read_csv(os.path.join(DATA_DIR, "genres.csv"))
    artists_df = pd.read_csv(os.path.join(DATA_DIR, "artists.csv"))
    users_df = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    return genres_df, artists_df, users_df


# -----------------------------------------------------------------------------
# Data-quality inspection
# -----------------------------------------------------------------------------

def inspect_user_data(users_df: pd.DataFrame) -> Dict[str, int]:
    """
    Inspect user-level fields without performing age analysis.

    We only measure whether age / top_genres are usable so the script can explain
    why the genre analysis moved to artist-level data.
    """
    if users_df.empty:
        return {
            "total_users": 0,
            "valid_age_rows": 0,
            "valid_user_genre_rows": 0,
        }

    age_series = pd.to_numeric(users_df.get("age"), errors="coerce").fillna(0)
    valid_age_rows = int((age_series > 0).sum())

    genre_series = users_df.get("top_genres")
    if genre_series is None:
        valid_user_genre_rows = 0
    else:
        valid_user_genre_rows = int(
            genre_series.fillna("").astype(str).str.strip().ne("").sum()
        )

    return {
        "total_users": int(len(users_df)),
        "valid_age_rows": valid_age_rows,
        "valid_user_genre_rows": valid_user_genre_rows,
    }


# -----------------------------------------------------------------------------
# Genre normalization
# -----------------------------------------------------------------------------

def normalize_label(label: object) -> str:
    """Standardize text labels before genre mapping."""
    text = str(label).strip().lower()
    if text in {"", "nan", "none"}:
        return ""

    replacements = {
        "_": " ",
        "/": " ",
        "–": "-",
        "—": "-",
        "hip hop": "hip-hop",
        "hiphop": "hip-hop",
        "rnb": "r&b",
        "rnb ": "r&b ",
        "trip hop": "trip-hop",
        "drum & bass": "drum and bass",
        "drum n bass": "drum and bass",
        "synth pop": "synth-pop",
        "electro pop": "electropop",
        "dance pop": "dance-pop",
        "nu-metal": "nu metal",
        "alt rock": "alternative rock",
        "indie-rock": "indie rock",
        "indie-pop": "indie pop",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = " ".join(text.split())
    return text



def canonicalize_genre(tag: object, valid_genres: Iterable[str]) -> Optional[str]:
    """
    Map raw artist tags to a cleaner genre vocabulary.

    Priority:
      1. Keep exact matches already present in genres.csv
      2. Collapse close variants / subgenres into a broad canonical family
      3. Return None if the tag is too noisy or not clearly a genre
    """
    tag = normalize_label(tag)
    if not tag:
        return None

    valid_genres = set(valid_genres)
    if tag in valid_genres:
        return tag

    explicit_map = {
        "alternative rock": "rock",
        "classic rock": "rock",
        "hard rock": "rock",
        "glam rock": "rock",
        "funk rock": "rock",
        "pop rock": "rock",
        "piano rock": "rock",
        "folk rock": "folk",
        "indie rock": "indie",
        "indie pop": "indie",
        "indie folk": "folk",
        "dream pop": "dream pop",
        "shoegaze": "shoegaze",
        "lo-fi": "lo-fi",
        "pop punk": "punk",
        "punk rock": "punk",
        "emo pop": "emo",
        "emo rock": "emo",
        "nu metal": "metal",
        "heavy metal": "metal",
        "thrash metal": "metal",
        "groove metal": "metal",
        "industrial metal": "metal",
        "alternative metal": "metal",
        "progressive metal": "metal",
        "metalcore": "metal",
        "melodic metalcore": "metal",
        "melodic death metal": "metal",
        "rap": "hip-hop",
        "pop rap": "hip-hop",
        "cloud rap": "hip-hop",
        "underground hip-hop": "hip-hop",
        "conscious hip hop": "hip-hop",
        "conscious hip-hop": "hip-hop",
        "west coast": "hip-hop",
        "dirty south": "hip-hop",
        "southern rap": "hip-hop",
        "alternative rap": "hip-hop",
        "hip hop": "hip-hop",
        "electropop": "pop",
        "dance-pop": "pop",
        "art pop": "pop",
        "alt-pop": "pop",
        "synthpop": "pop",
        "jazz pop": "jazz",
        "jazz fusion": "jazz",
        "cool jazz": "jazz",
        "free jazz": "jazz",
        "vocal jazz": "jazz",
        "avant-garde jazz": "jazz",
        "bebop": "jazz",
        "bossa nova": "jazz",
        "swing": "jazz",
        "electro": "electronic",
        "electronica": "electronic",
        "house music": "house",
        "tech house": "house",
        "new rave": "electronic",
        "2-step": "electronic",
        "disco house": "house",
        "electro house": "house",
        "singer songwriter": "singer-songwriter",
        "romantic": "classical",
        "baroque": "classical",
        "impressionist": "classical",
        "composers": "classical",
        "composer": "classical",
    }
    if tag in explicit_map:
        return explicit_map[tag]

    # Keyword-based fallbacks for tags not captured explicitly.
    keyword_rules = [
        (("k-pop",), "k-pop"),
        (("afrobeat", "afrobeats"), "afrobeats"),
        (("reggae",), "reggae"),
        (("latin", "reggaeton"), "latin"),
        (("country",), "country"),
        (("blues",), "blues"),
        (("soul",), "soul"),
        (("folk", "acoustic"), "folk"),
        (("classical", "baroque", "romantic", "composer"), "classical"),
        (("jazz", "bebop", "bossa nova", "swing"), "jazz"),
        (("r&b", "rhythm and blues"), "r&b"),
        (("hip-hop", "hip hop", "rap", "trap"), "hip-hop"),
        (("metal",), "metal"),
        (("punk",), "punk"),
        (("emo",), "emo"),
        (("grunge",), "grunge"),
        (("shoegaze",), "shoegaze"),
        (("dream pop",), "dream pop"),
        (("trip-hop",), "trip-hop"),
        (("dubstep",), "dubstep"),
        (("drum and bass",), "drum and bass"),
        (("techno",), "techno"),
        (("house",), "house"),
        (("dance", "electro", "electronica", "electronic"), "electronic"),
        (("indie",), "indie"),
        (("alternative",), "alternative"),
        (("rock", "britpop", "new wave", "garage rock", "progressive rock"), "rock"),
        (("experimental", "noise", "industrial", "gothic"), "experimental"),
        (("lo-fi",), "lo-fi"),
        (("soundtrack",), "soundtrack"),
        (("singer-songwriter",), "singer-songwriter"),
        (("psychedelic",), "psychedelic"),
        (("post-rock",), "post-rock"),
        (("post-punk",), "post-punk"),
        (("funk",), "funk"),
        (("ambient",), "ambient"),
    ]

    for keywords, genre in keyword_rules:
        if any(keyword in tag for keyword in keywords):
            return genre

    return None


# -----------------------------------------------------------------------------
# Artist-level genre preparation
# -----------------------------------------------------------------------------

def extract_primary_tag(top_tags_value: object) -> str:
    """Extract the first tag from a semicolon-separated Last.fm tag list."""
    if pd.isna(top_tags_value):
        return ""
    tags = [part.strip() for part in str(top_tags_value).split(";") if part.strip()]
    return tags[0] if tags else ""



def prepare_artist_genres(
    artists_df: pd.DataFrame,
    genres_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach a clean canonical genre to each artist and compute engagement metrics.

    We use the first artist tag as a genre proxy because it is typically the most
    representative label in the scraped Last.fm data.
    """
    df = artists_df.copy()
    df["listeners"] = pd.to_numeric(df["listeners"], errors="coerce").fillna(0)
    df["play_count"] = pd.to_numeric(df["play_count"], errors="coerce").fillna(0)

    valid_genres = {
        normalize_label(name)
        for name in genres_df["name"].dropna().astype(str)
    }

    df["primary_tag"] = df["top_tags"].apply(extract_primary_tag)
    df["main_genre"] = df["primary_tag"].apply(
        lambda x: canonicalize_genre(x, valid_genres)
    )

    df = df[df["main_genre"].notna()].copy()
    df = df[(df["listeners"] > 0) | (df["play_count"] > 0)].copy()
    df["loyalty_ratio"] = df["play_count"] / df["listeners"].clip(lower=1)

    return df



def build_genre_summary(artist_genres_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate artist-level data into genre-level metrics."""
    summary = (
        artist_genres_df.groupby("main_genre", as_index=False)
        .agg(
            artists_count=("name", "count"),
            total_listeners=("listeners", "sum"),
            total_play_count=("play_count", "sum"),
            mean_loyalty=("loyalty_ratio", "mean"),
            median_loyalty=("loyalty_ratio", "median"),
        )
    )

    summary["plays_per_listener"] = (
        summary["total_play_count"] / summary["total_listeners"].clip(lower=1)
    )

    total_listeners = summary["total_listeners"].sum()
    total_play_count = summary["total_play_count"].sum()
    summary["listener_share_pct"] = 100 * summary["total_listeners"] / max(total_listeners, 1)
    summary["play_share_pct"] = 100 * summary["total_play_count"] / max(total_play_count, 1)

    return summary.sort_values("total_listeners", ascending=False).reset_index(drop=True)


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------

def save_current_plot(filename: str) -> None:
    filepath = os.path.join(PLOTS_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")



def plot_genres_by_artist_count(summary_df: pd.DataFrame, top_n: int = 12) -> None:
    """Plot the genres most represented in the scraped artist sample."""
    top = summary_df.nlargest(top_n, "artists_count").sort_values("artists_count")

    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(top["main_genre"], top["artists_count"], edgecolor="white")
    ax.set_xlabel("Number of tagged artists", fontsize=12)
    ax.set_ylabel("Genre", fontsize=12)
    ax.set_title(
        f"Most Represented Genres in the Scraped Artist Sample (Top {top_n})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for bar, value in zip(bars, top["artists_count"]):
        ax.text(value + 0.15, bar.get_y() + bar.get_height() / 2, f"{value}", va="center")

    plt.tight_layout()
    save_current_plot("q1_genres_by_artist_count.png")



def plot_top_genres_by_listeners(summary_df: pd.DataFrame, top_n: int = 12) -> None:
    """Plot the genres with the largest combined listener base."""
    top = summary_df.nlargest(top_n, "total_listeners").sort_values("total_listeners")

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(top["main_genre"], top["total_listeners"], edgecolor="white")
    ax.set_xlabel("Total listeners across artists", fontsize=12)
    ax.set_ylabel("Genre", fontsize=12)
    ax.set_title(
        f"Main Genres by Total Listener Reach (Top {top_n})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    max_val = max(top["total_listeners"].max(), 1)
    for bar, value in zip(bars, top["total_listeners"]):
        ax.text(
            value + 0.01 * max_val,
            bar.get_y() + bar.get_height() / 2,
            f"{value / 1_000_000:.1f}M",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    save_current_plot("q1_top_genres_by_listeners.png")



def plot_top_genres_by_playcount(summary_df: pd.DataFrame, top_n: int = 12) -> None:
    """Plot the genres with the highest combined play count."""
    top = summary_df.nlargest(top_n, "total_play_count").sort_values("total_play_count")

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(top["main_genre"], top["total_play_count"], edgecolor="white")
    ax.set_xlabel("Total play count across artists", fontsize=12)
    ax.set_ylabel("Genre", fontsize=12)
    ax.set_title(
        f"Main Genres by Total Play Count (Top {top_n})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    max_val = max(top["total_play_count"].max(), 1)
    for bar, value in zip(bars, top["total_play_count"]):
        ax.text(
            value + 0.01 * max_val,
            bar.get_y() + bar.get_height() / 2,
            f"{value / 1_000_000_000:.2f}B",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    save_current_plot("q1_top_genres_by_playcount.png")



def plot_listener_share_vs_play_share(summary_df: pd.DataFrame, top_n: int = 12) -> None:
    """
    Compare genre reach and engagement.

    Genres above the diagonal generate a larger share of total plays than their
    share of total listeners would suggest.
    """
    top = summary_df.nlargest(top_n, "total_listeners").copy()

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        top["listener_share_pct"],
        top["play_share_pct"],
        s=top["artists_count"] * 65,
        c=top["plays_per_listener"],
        cmap="viridis",
        alpha=0.8,
        edgecolor="white",
        linewidth=0.7,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Plays per listener", fontsize=11)

    max_axis = float(max(top["listener_share_pct"].max(), top["play_share_pct"].max()) * 1.1)
    ax.plot([0, max_axis], [0, max_axis], "k--", linewidth=1.5, alpha=0.7, label="Equal share")

    for _, row in top.iterrows():
        ax.annotate(
            row["main_genre"],
            (row["listener_share_pct"], row["play_share_pct"]),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_xlim(0, max_axis)
    ax.set_ylim(0, max_axis)
    ax.set_xlabel("Share of total listeners (%)", fontsize=12)
    ax.set_ylabel("Share of total plays (%)", fontsize=12)
    ax.set_title(
        "Genre Reach vs. Genre Engagement",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.legend(fontsize=10)

    plt.tight_layout()
    save_current_plot("q1_genre_reach_vs_engagement.png")



def plot_loyalty_by_genre(artist_genres_df: pd.DataFrame, top_n: int = 10) -> None:
    """
    Plot artist-level loyalty distributions for the most important genres.

    Loyalty is approximated as play_count / listeners at the artist level.
    """
    top_genres = (
        artist_genres_df.groupby("main_genre")["listeners"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )

    plot_df = artist_genres_df[artist_genres_df["main_genre"].isin(top_genres)].copy()
    plot_df = plot_df[np.isfinite(plot_df["loyalty_ratio"])]
    plot_df = plot_df[plot_df["loyalty_ratio"] > 0]

    order = (
        plot_df.groupby("main_genre")["loyalty_ratio"]
        .median()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.boxplot(
        data=plot_df,
        x="main_genre",
        y="loyalty_ratio",
        order=order,
        ax=ax,
    )
    sns.stripplot(
        data=plot_df,
        x="main_genre",
        y="loyalty_ratio",
        order=order,
        ax=ax,
        color="black",
        alpha=0.35,
        size=4,
    )

    ax.set_xlabel("Genre", fontsize=12)
    ax.set_ylabel("Artist loyalty ratio (play_count / listeners)", fontsize=12)
    ax.set_title(
        "Artist-Level Engagement by Genre",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xticks(rotation=35, ha="right")

    plt.tight_layout()
    save_current_plot("q1_loyalty_by_genre.png")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("QUESTION 1: What Are the Main Musical Genres?")
    print("=" * 70)

    genres_df, artists_df, users_df = load_data()
    data_quality = inspect_user_data(users_df)
    artist_genres_df = prepare_artist_genres(artists_df, genres_df)
    summary_df = build_genre_summary(artist_genres_df)

    print(f"\nDatasets loaded:")
    print(f"  - genres.csv : {len(genres_df)} rows")
    print(f"  - artists.csv: {len(artists_df)} rows")
    print(f"  - users.csv  : {data_quality['total_users']} rows")

    print("\nData-quality check:")
    print(
        f"  - Users with valid age values: {data_quality['valid_age_rows']} / "
        f"{data_quality['total_users']}"
    )
    print(
        f"  - Users with non-empty top_genres: {data_quality['valid_user_genre_rows']} / "
        f"{data_quality['total_users']}"
    )
    print(
        "  - Result: age-based plots were removed, and user-level genre plots were "
        "replaced with artist/genre-based analysis."
    )

    print(f"\nArtists retained after genre cleaning: {len(artist_genres_df)}")
    print(f"Genres retained after normalization: {summary_df['main_genre'].nunique()}")

    print("\nGenerating plots...")
    plot_genres_by_artist_count(summary_df)
    plot_top_genres_by_listeners(summary_df)
    plot_top_genres_by_playcount(summary_df)
    plot_listener_share_vs_play_share(summary_df)
    plot_loyalty_by_genre(artist_genres_df)

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    print("\n1. Main genres by total listeners:")
    for _, row in summary_df.nlargest(5, "total_listeners").iterrows():
        print(
            f"   - {row['main_genre']}: {row['total_listeners'] / 1_000_000:.1f}M listeners "
            f"across {int(row['artists_count'])} artists"
        )

    print("\n2. Main genres by total play count:")
    for _, row in summary_df.nlargest(5, "total_play_count").iterrows():
        print(
            f"   - {row['main_genre']}: {row['total_play_count'] / 1_000_000_000:.2f}B plays"
        )

    represented = summary_df[summary_df["artists_count"] >= 3].copy()
    if not represented.empty:
        print("\n3. Genres with the deepest engagement (min. 3 artists):")
        for _, row in represented.nlargest(5, "plays_per_listener").iterrows():
            print(
                f"   - {row['main_genre']}: {row['plays_per_listener']:.1f} plays per listener"
            )

    print("\n4. Conclusion:")
    print(
        "   The revised analysis still answers the core genre question, but now uses "
        "the artist-tag data that is actually populated in the dataset."
    )
    print(
        "   In this scraped sample, the strongest genres are the ones that dominate "
        "listener volume, play volume, and artist representation."
    )
    print(
        "   The reach-vs-engagement and loyalty plots show that genre popularity and "
        "genre depth are not always the same thing: some genres attract broader audiences,"
    )
    print(
        "   while others generate more repeated listening per listener."
    )
    print()


if __name__ == "__main__":
    main()
