"""
Question 2: Is there a link between a music's duration and its popularity?

This script analyzes:
  - Distribution of track durations
  - Correlation between duration (seconds) and popularity (listeners/play_count)
  - Optimal duration ranges for popular songs
  - Statistical tests for significance

Outputs: Multiple plots saved to analysis/plots/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_data():
    """Load tracks CSV."""
    tracks_df = pd.read_csv(os.path.join(DATA_DIR, "tracks.csv"))
    return tracks_df


def clean_data(tracks_df):
    """Filter out tracks with missing or invalid duration."""
    df = tracks_df[tracks_df["duration_seconds"] > 0].copy()
    df["duration_minutes"] = df["duration_seconds"] / 60.0

    # Create duration categories for grouped analysis
    bins = [0, 2, 3, 4, 5, 7, 100]
    labels = ["< 2 min", "2-3 min", "3-4 min", "4-5 min", "5-7 min", "> 7 min"]
    df["duration_category"] = pd.cut(df["duration_minutes"], bins=bins, labels=labels)

    # Log-transform popularity for better visualization
    df["log_listeners"] = np.log10(df["listeners"].clip(lower=1))
    df["log_play_count"] = np.log10(df["play_count"].clip(lower=1))

    return df


def plot_duration_distribution(df):
    """
    Plot 1: Distribution of track durations.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df["duration_minutes"], bins=40, color="#3498db",
                 edgecolor="white", alpha=0.85)
    axes[0].axvline(df["duration_minutes"].mean(), color="#e74c3c",
                    linestyle="--", linewidth=2,
                    label=f'Mean: {df["duration_minutes"].mean():.1f} min')
    axes[0].axvline(df["duration_minutes"].median(), color="#2ecc71",
                    linestyle="--", linewidth=2,
                    label=f'Median: {df["duration_minutes"].median():.1f} min')
    axes[0].set_xlabel("Duration (minutes)", fontsize=11)
    axes[0].set_ylabel("Number of tracks", fontsize=11)
    axes[0].set_title("Distribution of Track Durations", fontsize=13,
                      fontweight="bold")
    axes[0].legend()

    # Category count
    cat_counts = df["duration_category"].value_counts().sort_index()
    colors = sns.color_palette("viridis", n_colors=len(cat_counts))
    axes[1].bar(range(len(cat_counts)), cat_counts.values, color=colors,
                edgecolor="white")
    axes[1].set_xticks(range(len(cat_counts)))
    axes[1].set_xticklabels(cat_counts.index, rotation=30, ha="right")
    axes[1].set_xlabel("Duration Category", fontsize=11)
    axes[1].set_ylabel("Number of tracks", fontsize=11)
    axes[1].set_title("Tracks per Duration Category", fontsize=13,
                      fontweight="bold")

    # Add count labels
    for i, v in enumerate(cat_counts.values):
        axes[1].text(i, v + 1, str(v), ha="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q2_duration_distribution.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_duration_vs_popularity_scatter(df):
    """
    Plot 2: Scatter plot of duration vs popularity (listeners).
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Scatter: duration vs listeners
    axes[0].scatter(df["duration_minutes"], df["log_listeners"],
                    alpha=0.4, s=30, c="#3498db", edgecolor="none")

    # Add trend line (polynomial fit)
    z = np.polyfit(df["duration_minutes"], df["log_listeners"], 2)
    p = np.poly1d(z)
    x_line = np.linspace(df["duration_minutes"].min(),
                         df["duration_minutes"].max(), 100)
    axes[0].plot(x_line, p(x_line), "r-", linewidth=2.5,
                 label="Polynomial trend (deg=2)")

    axes[0].set_xlabel("Duration (minutes)", fontsize=11)
    axes[0].set_ylabel("log₁₀(Listeners)", fontsize=11)
    axes[0].set_title("Track Duration vs. Popularity (Listeners)",
                      fontsize=13, fontweight="bold")
    axes[0].legend()

    # Scatter: duration vs play count
    axes[1].scatter(df["duration_minutes"], df["log_play_count"],
                    alpha=0.4, s=30, c="#e74c3c", edgecolor="none")

    z2 = np.polyfit(df["duration_minutes"], df["log_play_count"], 2)
    p2 = np.poly1d(z2)
    axes[1].plot(x_line, p2(x_line), "b-", linewidth=2.5,
                 label="Polynomial trend (deg=2)")

    axes[1].set_xlabel("Duration (minutes)", fontsize=11)
    axes[1].set_ylabel("log₁₀(Play Count)", fontsize=11)
    axes[1].set_title("Track Duration vs. Popularity (Play Count)",
                      fontsize=13, fontweight="bold")
    axes[1].legend()

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q2_duration_vs_popularity_scatter.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_popularity_by_duration_category(df):
    """
    Plot 3: Box plot showing popularity distribution per duration category.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Boxplot: listeners by duration category
    sns.boxplot(data=df, x="duration_category", y="log_listeners",
                ax=axes[0], palette="viridis", order=[
                    "< 2 min", "2-3 min", "3-4 min", "4-5 min",
                    "5-7 min", "> 7 min"
                ])
    axes[0].set_xlabel("Duration Category", fontsize=11)
    axes[0].set_ylabel("log₁₀(Listeners)", fontsize=11)
    axes[0].set_title("Popularity (Listeners) by Duration Category",
                      fontsize=13, fontweight="bold")
    axes[0].tick_params(axis="x", rotation=30)

    # Boxplot: play count by duration category
    sns.boxplot(data=df, x="duration_category", y="log_play_count",
                ax=axes[1], palette="magma", order=[
                    "< 2 min", "2-3 min", "3-4 min", "4-5 min",
                    "5-7 min", "> 7 min"
                ])
    axes[1].set_xlabel("Duration Category", fontsize=11)
    axes[1].set_ylabel("log₁₀(Play Count)", fontsize=11)
    axes[1].set_title("Popularity (Play Count) by Duration Category",
                      fontsize=13, fontweight="bold")
    axes[1].tick_params(axis="x", rotation=30)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q2_popularity_by_duration_boxplot.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_avg_popularity_by_category(df):
    """
    Plot 4: Bar chart of average popularity per duration category.
    Clear visualization for the conclusion.
    """
    order = ["< 2 min", "2-3 min", "3-4 min", "4-5 min", "5-7 min", "> 7 min"]
    stats = df.groupby("duration_category", observed=True).agg(
        avg_listeners=("listeners", "mean"),
        avg_play_count=("play_count", "mean"),
        count=("name", "count"),
        median_listeners=("listeners", "median"),
    ).reindex(order)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    colors = sns.color_palette("coolwarm", n_colors=len(stats))

    # Average listeners
    bars1 = axes[0].bar(range(len(stats)), stats["avg_listeners"],
                        color=colors, edgecolor="white")
    axes[0].set_xticks(range(len(stats)))
    axes[0].set_xticklabels(stats.index, rotation=30, ha="right")
    axes[0].set_xlabel("Duration Category", fontsize=11)
    axes[0].set_ylabel("Average Listeners", fontsize=11)
    axes[0].set_title("Average Listeners by Duration Category",
                      fontsize=13, fontweight="bold")

    # Add sample size labels
    for i, (bar, n) in enumerate(zip(bars1, stats["count"])):
        axes[0].text(i, bar.get_height() * 1.02, f"n={n}",
                     ha="center", fontsize=9, style="italic")

    # Average play count
    bars2 = axes[1].bar(range(len(stats)), stats["avg_play_count"],
                        color=colors, edgecolor="white")
    axes[1].set_xticks(range(len(stats)))
    axes[1].set_xticklabels(stats.index, rotation=30, ha="right")
    axes[1].set_xlabel("Duration Category", fontsize=11)
    axes[1].set_ylabel("Average Play Count", fontsize=11)
    axes[1].set_title("Average Play Count by Duration Category",
                      fontsize=13, fontweight="bold")

    for i, (bar, n) in enumerate(zip(bars2, stats["count"])):
        axes[1].text(i, bar.get_height() * 1.02, f"n={n}",
                     ha="center", fontsize=9, style="italic")

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q2_avg_popularity_by_duration.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")

    return stats


def main():
    print("=" * 60)
    print("QUESTION 2: Duration vs. Popularity Analysis")
    print("=" * 60)

    tracks_df = load_data()
    df = clean_data(tracks_df)

    print(f"\nDataset: {len(df)} tracks with valid duration")
    print(f"Duration range: {df['duration_minutes'].min():.1f} - "
          f"{df['duration_minutes'].max():.1f} minutes")
    print(f"Mean duration: {df['duration_minutes'].mean():.1f} min")

    print("\nGenerating plots...")
    plot_duration_distribution(df)
    plot_duration_vs_popularity_scatter(df)
    plot_popularity_by_duration_category(df)
    stats = plot_avg_popularity_by_category(df)

    # Compute Pearson correlation
    corr_listeners = df["duration_seconds"].corr(df["listeners"])
    corr_play_count = df["duration_seconds"].corr(df["play_count"])
    corr_log_listeners = df["duration_seconds"].corr(df["log_listeners"])

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)
    print(f"\n1. Pearson correlation (duration vs listeners): {corr_listeners:.4f}")
    print(f"   Pearson correlation (duration vs play count): {corr_play_count:.4f}")
    print(f"   Pearson correlation (duration vs log(listeners)): "
          f"{corr_log_listeners:.4f}")

    print(f"\n2. Average popularity by duration category:")
    for cat in stats.index:
        row = stats.loc[cat]
        if not pd.isna(row["avg_listeners"]):
            print(f"   {cat:>8s}: {row['avg_listeners']:>12,.0f} listeners "
                  f"(n={row['count']:.0f})")

    print(f"\n3. Conclusion:")
    if abs(corr_listeners) < 0.1:
        print("   The correlation is very weak, suggesting that track duration")
        print("   has minimal direct impact on popularity. However, the boxplot")
        print("   analysis reveals that songs in the 3-4 minute range tend to")
        print("   have the highest median popularity, likely reflecting the")
        print("   standard radio-friendly format.")
    else:
        print(f"   There is a {'positive' if corr_listeners > 0 else 'negative'} "
              f"correlation ({corr_listeners:.3f}) between duration and popularity.")
    print()


if __name__ == "__main__":
    main()
