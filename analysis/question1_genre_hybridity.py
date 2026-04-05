"""
Question 1: Which musical genres are the most hybrid in our scraped Last.fm dataset?

This script analyzes:
  - Which genres co-occur with the largest variety of other genres
  - Which genres most frequently appear in mixed tag profiles
  - The most common genre pairings
  - The overall co-occurrence structure between major genres

Outputs: Multiple plots saved to analysis/plots/
"""

import os
from collections import Counter, defaultdict
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_data():
    """Load artists CSV."""
    artists_df = pd.read_csv(os.path.join(DATA_DIR, "artists.csv"))
    return artists_df


def parse_tags(tag_string, max_tags=5):
    """
    Parse the semicolon-separated top_tags column.

    Keeps order, removes duplicates, normalizes case, and ignores empty values.
    """
    if pd.isna(tag_string):
        return []

    seen = set()
    tags = []
    for raw_tag in str(tag_string).split(";"):
        tag = raw_tag.strip().lower()
        if not tag:
            continue
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)

    # Limit tags per artist to avoid inflating co-occurrence counts
    return tags[:max_tags]


def build_genre_structures(df):
    """
    Build reusable genre statistics from artist tag lists.
    """
    df = df.copy()
    df["parsed_tags"] = df["top_tags"].apply(parse_tags)
    df = df[df["parsed_tags"].map(len) > 0].copy()  # drop artists with no tags

    genre_frequency = Counter()        # number of artists per genre
    unique_partners = defaultdict(set) # distinct genres each genre co-occurs with
    total_cooccurrence = Counter()     # total number of pairings per genre
    pair_counts = Counter()            # how many artists share each genre pair

    for tags in df["parsed_tags"]:
        for tag in tags:
            genre_frequency[tag] += 1

        if len(tags) < 2:
            continue  # need at least 2 tags to form a pair

        # sorted() keeps pairs in alphabetical order to avoid counting (a,b) and (b,a) separately
        for a, b in combinations(sorted(tags), 2):
            pair_counts[(a, b)] += 1
            unique_partners[a].add(b)
            unique_partners[b].add(a)
            total_cooccurrence[a] += 1
            total_cooccurrence[b] += 1

    hybrid_rows = []
    for genre, artist_count in genre_frequency.items():
        hybrid_rows.append(
            {
                "genre": genre,
                "artist_count": artist_count,
                "unique_partner_count": len(unique_partners.get(genre, set())),
                "total_cooccurrence_count": total_cooccurrence.get(genre, 0),
                # average number of co-occurrences per artist
                "hybridity_ratio": (
                    total_cooccurrence.get(genre, 0) / artist_count if artist_count > 0 else 0
                ),
            }
        )

    # Sort by diversity first, then by volume
    genre_stats = pd.DataFrame(hybrid_rows).sort_values(
        ["unique_partner_count", "total_cooccurrence_count", "artist_count"],
        ascending=False,
    )

    pair_df = pd.DataFrame(
        [
            {"genre_a": a, "genre_b": b, "count": count}
            for (a, b), count in pair_counts.items()
        ]
    ).sort_values("count", ascending=False)

    return df, genre_stats, pair_df, genre_frequency


def plot_unique_partner_count(genre_stats, top_n=15):
    """
    Plot 1: Genres with the widest diversity of co-occurring genres.
    """
    top = genre_stats.nlargest(top_n, "unique_partner_count").sort_values(
        "unique_partner_count", ascending=True
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(top)),
        top["unique_partner_count"].values,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["genre"].values, fontsize=10)
    ax.set_xlabel("Number of unique co-occurring genres", fontsize=12)
    ax.set_title(
        "Genres with the Largest Variety of Cross-Genre Connections",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, (bar, artist_count) in enumerate(zip(bars, top["artist_count"].values)):
        ax.text(
            bar.get_width() + 0.1,
            i,
            f"artists={artist_count}",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q1_hybrid_genres_unique_partners.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_total_cooccurrence_count(genre_stats, top_n=15):
    """
    Plot 2: Genres that most frequently appear in mixed genre profiles.
    """
    top = genre_stats.nlargest(top_n, "total_cooccurrence_count").sort_values(
        "total_cooccurrence_count", ascending=True
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(top)),
        top["total_cooccurrence_count"].values,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["genre"].values, fontsize=10)
    ax.set_xlabel("Total genre co-occurrence count", fontsize=12)
    ax.set_title(
        "Genres That Most Frequently Appear in Mixed Tag Profiles",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, (bar, ratio) in enumerate(zip(bars, top["hybridity_ratio"].values)):
        ax.text(
            bar.get_width() + 0.1,
            i,
            f"ratio={ratio:.2f}",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q1_hybrid_genres_total_cooccurrences.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_top_genre_pairs(pair_df, top_n=15):
    """
    Plot 3: Most frequent genre pairs in the dataset.
    """
    top_pairs = pair_df.head(top_n).copy()
    top_pairs["pair_label"] = top_pairs["genre_a"] + " + " + top_pairs["genre_b"]
    top_pairs = top_pairs.sort_values("count", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(top_pairs)),
        top_pairs["count"].values,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(top_pairs)))
    ax.set_yticklabels(top_pairs["pair_label"].values, fontsize=10)
    ax.set_xlabel("Number of artists where the pair appears together", fontsize=12)
    ax.set_title(
        "Most Frequent Genre Pairings in the Dataset",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, bar in enumerate(bars):
        ax.text(
            bar.get_width() + 0.1,
            i,
            f"{int(bar.get_width())}",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q1_top_genre_pairs.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_genre_cooccurrence_heatmap(parsed_df, genre_frequency, top_n=12):
    """
    Plot 4: Heatmap of co-occurrence among the most frequent genres.
    """
    top_genres = [genre for genre, _ in genre_frequency.most_common(top_n)]
    # matrix[a][b] = number of artists carrying both genre a and genre b
    matrix = pd.DataFrame(0, index=top_genres, columns=top_genres, dtype=int)

    for tags in parsed_df["parsed_tags"]:
        filtered = [tag for tag in tags if tag in top_genres]
        filtered = list(dict.fromkeys(filtered))  # deduplicate, preserve order

        for tag in filtered:
            matrix.loc[tag, tag] += 1  # diagonal: solo presence count

        for a, b in combinations(filtered, 2):
            matrix.loc[a, b] += 1  # symmetric update for a valid co-occurrence matrix
            matrix.loc[b, a] += 1

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Co-occurrence count"},
    )
    ax.set_xlabel("Genre", fontsize=12)
    ax.set_ylabel("Genre", fontsize=12)
    ax.set_title(
        "Genre Co-occurrence Heatmap (Top Genres)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q1_genre_cooccurrence_heatmap.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def main():
    print("=" * 60)
    print("QUESTION 1: Which Genres Are the Most Hybrid?")
    print("=" * 60)

    artists_df = load_data()
    parsed_df, genre_stats, pair_df, genre_frequency = build_genre_structures(artists_df)

    print(f"\nDataset: {len(parsed_df)} artists with valid genre tags")
    print(f"Unique genres found: {genre_stats['genre'].nunique()}")
    print(
        f"Average number of tags per artist: "
        f"{parsed_df['parsed_tags'].map(len).mean():.2f}"
    )

    print("\nGenerating plots...")
    plot_unique_partner_count(genre_stats)
    plot_total_cooccurrence_count(genre_stats)
    plot_top_genre_pairs(pair_df)
    plot_genre_cooccurrence_heatmap(parsed_df, genre_frequency)

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)

    print("\n1. Most hybrid genres by unique partner diversity:")
    for _, row in genre_stats.nlargest(5, "unique_partner_count").iterrows():
        print(
            f"   - {row['genre']}: {int(row['unique_partner_count'])} unique partners "
            f"across {int(row['artist_count'])} artists"
        )

    print("\n2. Most hybrid genres by total mixing intensity:")
    for _, row in genre_stats.nlargest(5, "total_cooccurrence_count").iterrows():
        print(
            f"   - {row['genre']}: {int(row['total_cooccurrence_count'])} total "
            f"co-occurrences (ratio={row['hybridity_ratio']:.2f})"
        )

    print("\n3. Most frequent genre pairs:")
    for _, row in pair_df.head(5).iterrows():
        print(f"   - {row['genre_a']} + {row['genre_b']}: {int(row['count'])}")

    print("\n4. Conclusion:")
    print("   Some genres act as hybrid hubs because they repeatedly mix with")
    print("   many other styles across artist tag profiles. Instead of forming")
    print("   isolated musical categories, the dataset reveals a strong network")
    print("   of overlapping genre identities, especially around broad genres")
    print("   such as alternative, indie, pop, rock, and electronic.")
    print()


if __name__ == "__main__":
    main()
