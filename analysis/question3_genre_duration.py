"""
Question 3: Are songs from some genres systematically longer than songs from
others on Last.fm?

This script analyzes:
  - The average and median duration of tracks by primary genre
  - The distribution of track duration across major genres
  - Which genres contain the longest tracks on average
  - Whether some genres show much wider duration variability than others

Outputs: Multiple plots saved to analysis/plots/
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

MIN_TRACKS_PER_GENRE = 12
TOP_GENRES_FOR_DISTRIBUTION = 10


def load_data():
    """Load tracks CSV."""
    return pd.read_csv(os.path.join(DATA_DIR, "tracks.csv"))


def parse_tags(tag_string):
    """Parse semicolon-separated track tags."""
    if pd.isna(tag_string):
        return []

    seen = set()
    tags = []
    for raw_tag in str(tag_string).split(";"):
        tag = raw_tag.strip().lower()
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def prepare_data(tracks_df):
    """
    Keep only tracks with usable duration and genre tags, and derive genre features.
    """
    df = tracks_df.copy()
    df = df[df["duration_seconds"] > 0].copy()  # 0 means extraction failed
    df["parsed_tags"] = df["tags"].apply(parse_tags)
    df = df[df["parsed_tags"].map(len) > 0].copy()  # drop tracks with no genre

    # First tag is used as primary genre (most representative label on Last.fm)
    df["primary_genre"] = df["parsed_tags"].map(lambda tags: tags[0])
    df["duration_minutes"] = df["duration_seconds"] / 60.0

    # data_quality may be read as string by pandas depending on CSV quoting
    if "data_quality" in df.columns:
        df["data_quality"] = pd.to_numeric(df["data_quality"], errors="coerce").fillna(0.0)
    else:
        df["data_quality"] = 0.0

    # Keep only genres with enough tracks to compute reliable statistics
    genre_counts = df["primary_genre"].value_counts()
    valid_genres = genre_counts[genre_counts >= MIN_TRACKS_PER_GENRE].index
    df = df[df["primary_genre"].isin(valid_genres)].copy()

    return df


def build_genre_summary(df):
    """Aggregate duration statistics by primary genre."""
    summary = (
        df.groupby("primary_genre", observed=True)
        .agg(
            track_count=("name", "count"),
            avg_duration_seconds=("duration_seconds", "mean"),
            median_duration_seconds=("duration_seconds", "median"),
            std_duration_seconds=("duration_seconds", "std"),
            avg_listeners=("listeners", "mean"),
            avg_data_quality=("data_quality", "mean"),
        )
        .reset_index()
    )
    summary["avg_duration_minutes"] = summary["avg_duration_seconds"] / 60.0
    summary["median_duration_minutes"] = summary["median_duration_seconds"] / 60.0
    summary["std_duration_minutes"] = summary["std_duration_seconds"].fillna(0.0) / 60.0
    return summary.sort_values(["avg_duration_seconds", "track_count"], ascending=False)


def plot_average_duration_by_genre(summary):
    """
    Plot 1: Average track duration by genre.
    """
    plot_df = summary.sort_values("avg_duration_minutes", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(plot_df)),
        plot_df["avg_duration_minutes"].values,
        color=sns.color_palette("crest", n_colors=len(plot_df)),
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df["primary_genre"].values, fontsize=10)
    ax.set_xlabel("Average duration (minutes)", fontsize=12)
    ax.set_title(
        "Average Track Duration by Primary Genre",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, (bar, n) in enumerate(zip(bars, plot_df["track_count"].values)):
        ax.text(bar.get_width() + 0.03, i, f"n={n}", va="center", fontsize=9)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_avg_duration_by_genre.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_duration_distribution_by_genre(df, summary):
    """
    Plot 2: Duration distribution for the most represented genres.
    """
    top_genres = (
        summary.sort_values("track_count", ascending=False)
        .head(TOP_GENRES_FOR_DISTRIBUTION)["primary_genre"]
        .tolist()
    )
    plot_df = df[df["primary_genre"].isin(top_genres)].copy()

    order = (
        plot_df.groupby("primary_genre", observed=True)["duration_minutes"]
        .median()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    fig, ax = plt.subplots(figsize=(13, 7))
    sns.boxplot(
        data=plot_df,
        x="primary_genre",
        y="duration_minutes",
        hue="primary_genre",
        order=order,
        palette="Set2",
        legend=False,
        ax=ax,
    )

    ax.set_xlabel("Primary genre", fontsize=12)
    ax.set_ylabel("Track duration (minutes)", fontsize=12)
    ax.set_title(
        "Duration Distribution Across Major Genres",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.tick_params(axis="x", rotation=35)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_duration_distribution_by_genre.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_longest_genres(summary, top_n=12):
    """
    Plot 3: Genres with the longest average tracks.
    """
    plot_df = summary.head(top_n).sort_values("avg_duration_minutes", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(plot_df)),
        plot_df["avg_duration_minutes"].values,
        color=sns.color_palette("mako", n_colors=len(plot_df)),
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df["primary_genre"].values, fontsize=10)
    ax.set_xlabel("Average duration (minutes)", fontsize=12)
    ax.set_title(
        "Genres With the Longest Tracks on Average",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, (bar, median_value) in enumerate(zip(bars, plot_df["median_duration_minutes"].values)):
        ax.text(bar.get_width() + 0.03, i, f"median={median_value:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_longest_genres.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_duration_variability(summary, top_n=12):
    """
    Plot 4: Variability of durations by genre.
    """
    plot_df = summary.sort_values("std_duration_minutes", ascending=False).head(top_n)
    plot_df = plot_df.sort_values("std_duration_minutes", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        range(len(plot_df)),
        plot_df["std_duration_minutes"].values,
        color=sns.color_palette("flare", n_colors=len(plot_df)),
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df["primary_genre"].values, fontsize=10)
    ax.set_xlabel("Standard deviation of duration (minutes)", fontsize=12)
    ax.set_title(
        "Genres With the Widest Duration Variability",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    for i, (bar, n) in enumerate(zip(bars, plot_df["track_count"].values)):
        ax.text(bar.get_width() + 0.03, i, f"n={n}", va="center", fontsize=9)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_duration_variability_by_genre.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def main():
    print("=" * 60)
    print("QUESTION 3: Are Songs From Some Genres Systematically Longer?")
    print("=" * 60)

    tracks_df = load_data()
    df = prepare_data(tracks_df)
    summary = build_genre_summary(df)

    print(f"\nDataset: {len(df)} tracks with valid duration and primary genre")
    print(f"Genres retained (min {MIN_TRACKS_PER_GENRE} tracks): {len(summary)}")
    print(
        f"Overall duration range: {df['duration_minutes'].min():.2f} - "
        f"{df['duration_minutes'].max():.2f} minutes"
    )

    print("\nGenerating plots...")
    plot_average_duration_by_genre(summary)
    plot_duration_distribution_by_genre(df, summary)
    plot_longest_genres(summary)
    plot_duration_variability(summary)

    shortest = summary.sort_values("avg_duration_seconds", ascending=True).head(5)
    longest = summary.head(5)
    most_variable = summary.sort_values("std_duration_seconds", ascending=False).head(5)

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)

    print("\n1. Genres with the longest tracks on average:")
    for _, row in longest.iterrows():
        print(
            f"   - {row['primary_genre']}: {row['avg_duration_minutes']:.2f} min "
            f"(median={row['median_duration_minutes']:.2f}, n={int(row['track_count'])})"
        )

    print("\n2. Genres with the shortest tracks on average:")
    for _, row in shortest.iterrows():
        print(
            f"   - {row['primary_genre']}: {row['avg_duration_minutes']:.2f} min "
            f"(median={row['median_duration_minutes']:.2f}, n={int(row['track_count'])})"
        )

    print("\n3. Genres with the widest duration variability:")
    for _, row in most_variable.iterrows():
        print(
            f"   - {row['primary_genre']}: std={row['std_duration_minutes']:.2f} min "
            f"(n={int(row['track_count'])})"
        )

    longest_genre = longest.iloc[0]
    shortest_genre = shortest.iloc[0]
    duration_gap = longest_genre["avg_duration_minutes"] - shortest_genre["avg_duration_minutes"]

    print("\n4. Conclusion:")
    print(
        f"   Yes. In this Last.fm sample, track duration differs meaningfully across "
        f"genres. The gap between the longest and shortest average genres is about "
        f"{duration_gap:.2f} minutes, which suggests that genre is associated with "
        f"clear differences in song format and structure."
    )
    print()


if __name__ == "__main__":
    main()
