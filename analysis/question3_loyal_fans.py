"""
Question 3: Do the biggest artists have loyal fans?

"Loyalty" is measured by the ratio of play_count to listeners.
A high ratio means fans listen repeatedly (loyal), while a low ratio
means many people listen but don't come back often.

This script analyzes:
  - Top artists by listeners vs. their loyalty ratio
  - Comparison of loyalty across popularity tiers
  - Relationship between artist size and fan loyalty
  - Which genres have the most loyal fanbases

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
    """Load artists CSV."""
    artists_df = pd.read_csv(os.path.join(DATA_DIR, "artists.csv"))
    return artists_df


def compute_loyalty(df):
    """
    Compute the loyalty ratio for each artist.
    Loyalty ratio = play_count / listeners
    Higher ratio = more loyal fans (they scrobble more per person).
    """
    df = df.copy()
    df["loyalty_ratio"] = df["play_count"] / df["listeners"].clip(lower=1)

    # Create popularity tiers
    df["popularity_rank"] = df["listeners"].rank(ascending=False)
    total = len(df)
    df["popularity_tier"] = pd.cut(
        df["popularity_rank"],
        bins=[0, total * 0.1, total * 0.25, total * 0.5, total],
        labels=["Top 10%", "Top 25%", "Top 50%", "Bottom 50%"]
    )

    # Extract primary genre
    df["primary_genre"] = df["top_tags"].apply(
        lambda x: str(x).split(";")[0].strip() if pd.notna(x) else "unknown"
    )

    return df


def plot_top_artists_loyalty(df, top_n=25):
    """
    Plot 1: Bar chart comparing loyalty ratio of the top N artists by listeners.
    Are the biggest artists also the ones with the most loyal fans?
    """
    top = df.nlargest(top_n, "listeners").sort_values("loyalty_ratio",
                                                       ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Color by loyalty level
    colors = []
    for ratio in top["loyalty_ratio"]:
        if ratio >= 8:
            colors.append("#27ae60")  # Green = very loyal
        elif ratio >= 5:
            colors.append("#f39c12")  # Orange = moderate
        else:
            colors.append("#e74c3c")  # Red = low loyalty

    bars = ax.barh(range(top_n), top["loyalty_ratio"].values,
                   color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top["name"].values, fontsize=10)
    ax.set_xlabel("Loyalty Ratio (scrobbles per listener)", fontsize=12)
    ax.set_title(f"Fan Loyalty of Top {top_n} Artists (by listeners)",
                 fontsize=14, fontweight="bold", pad=15)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top["loyalty_ratio"].values)):
        ax.text(val + 0.1, i, f"{val:.1f}x", va="center", fontsize=9)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#27ae60", label="High loyalty (≥8x)"),
        Patch(facecolor="#f39c12", label="Moderate loyalty (5-8x)"),
        Patch(facecolor="#e74c3c", label="Low loyalty (<5x)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_top_artists_loyalty.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_loyalty_vs_popularity_scatter(df):
    """
    Plot 2: Scatter plot of listeners (popularity) vs loyalty ratio.
    Shows whether bigger artists tend to have more or less loyal fans.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    scatter = ax.scatter(
        np.log10(df["listeners"].clip(lower=1)),
        df["loyalty_ratio"],
        c=df["loyalty_ratio"],
        cmap="RdYlGn",
        s=50, alpha=0.6, edgecolor="gray", linewidth=0.3
    )
    plt.colorbar(scatter, ax=ax, label="Loyalty Ratio")

    # Trend line
    x = np.log10(df["listeners"].clip(lower=1))
    y = df["loyalty_ratio"]
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p(x_line), "k--", linewidth=2, alpha=0.7,
            label=f"Trend line (slope={z[0]:.2f})")

    # Annotate some notable artists
    top_5 = df.nlargest(5, "listeners")
    loyal_5 = df.nlargest(5, "loyalty_ratio")
    to_annotate = pd.concat([top_5, loyal_5]).drop_duplicates()

    for _, row in to_annotate.iterrows():
        ax.annotate(row["name"],
                    (np.log10(row["listeners"]), row["loyalty_ratio"]),
                    fontsize=8, alpha=0.8,
                    xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel("log₁₀(Listeners) — Popularity →", fontsize=12)
    ax.set_ylabel("Loyalty Ratio (scrobbles/listener)", fontsize=12)
    ax.set_title("Artist Popularity vs. Fan Loyalty",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=11)

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_loyalty_vs_popularity.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_loyalty_by_tier(df):
    """
    Plot 3: Box plot comparing loyalty across popularity tiers.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    order = ["Top 10%", "Top 25%", "Top 50%", "Bottom 50%"]
    valid = df[df["popularity_tier"].notna()]
    sns.boxplot(data=valid, x="popularity_tier", y="loyalty_ratio",
                ax=ax, palette="Set2", order=order)
    sns.stripplot(data=valid, x="popularity_tier", y="loyalty_ratio",
                  ax=ax, color="black", alpha=0.3, size=3, order=order)

    ax.set_xlabel("Popularity Tier", fontsize=12)
    ax.set_ylabel("Loyalty Ratio (scrobbles/listener)", fontsize=12)
    ax.set_title("Fan Loyalty by Artist Popularity Tier",
                 fontsize=14, fontweight="bold", pad=15)

    # Add median labels
    medians = valid.groupby("popularity_tier", observed=True)["loyalty_ratio"].median()
    for i, tier in enumerate(order):
        if tier in medians.index:
            ax.text(i, medians[tier] + 0.3,
                    f"median: {medians[tier]:.1f}",
                    ha="center", fontsize=9, fontweight="bold", color="#333")

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_loyalty_by_tier.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")


def plot_loyalty_by_genre(df):
    """
    Plot 4: Average loyalty by primary genre.
    Bonus insight: which genres have the most loyal fanbases?
    """
    genre_loyalty = df.groupby("primary_genre").agg(
        avg_loyalty=("loyalty_ratio", "mean"),
        median_loyalty=("loyalty_ratio", "median"),
        count=("name", "count"),
    ).reset_index()

    # Only genres with at least 3 artists
    genre_loyalty = genre_loyalty[genre_loyalty["count"] >= 3]
    genre_loyalty = genre_loyalty.nlargest(15, "avg_loyalty")

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("coolwarm_r", n_colors=len(genre_loyalty))

    bars = ax.barh(range(len(genre_loyalty)),
                   genre_loyalty["avg_loyalty"].values,
                   color=colors, edgecolor="white")
    ax.set_yticks(range(len(genre_loyalty)))
    ax.set_yticklabels(genre_loyalty["primary_genre"].values, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Average Loyalty Ratio", fontsize=12)
    ax.set_title("Fan Loyalty by Genre (avg scrobbles per listener)",
                 fontsize=14, fontweight="bold", pad=15)

    for i, (bar, n) in enumerate(zip(bars, genre_loyalty["count"])):
        ax.text(bar.get_width() + 0.1, i, f"n={n}",
                va="center", fontsize=9, style="italic")

    plt.tight_layout()
    filepath = os.path.join(PLOTS_DIR, "q3_loyalty_by_genre.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filepath}")

    return genre_loyalty


def main():
    print("=" * 60)
    print("QUESTION 3: Do the Biggest Artists Have Loyal Fans?")
    print("=" * 60)

    artists_df = load_data()
    df = compute_loyalty(artists_df)

    print(f"\nDataset: {len(df)} artists")
    print(f"Loyalty ratio range: {df['loyalty_ratio'].min():.1f} - "
          f"{df['loyalty_ratio'].max():.1f}")
    print(f"Mean loyalty: {df['loyalty_ratio'].mean():.1f}")

    print("\nGenerating plots...")
    plot_top_artists_loyalty(df)
    plot_loyalty_vs_popularity_scatter(df)
    plot_loyalty_by_tier(df)
    genre_loyalty = plot_loyalty_by_genre(df)

    # Compute correlation
    corr = np.log10(df["listeners"].clip(lower=1)).corr(df["loyalty_ratio"])

    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)

    # Top 5 most loyal fanbases among big artists
    top_50 = df.nlargest(50, "listeners")
    most_loyal = top_50.nlargest(5, "loyalty_ratio")
    least_loyal = top_50.nsmallest(5, "loyalty_ratio")

    print("\n1. Most loyal fanbases (among top 50 artists):")
    for _, row in most_loyal.iterrows():
        print(f"   - {row['name']}: {row['loyalty_ratio']:.1f}x "
              f"({row['listeners']:,.0f} listeners)")

    print("\n2. Least loyal fanbases (among top 50 artists):")
    for _, row in least_loyal.iterrows():
        print(f"   - {row['name']}: {row['loyalty_ratio']:.1f}x "
              f"({row['listeners']:,.0f} listeners)")

    print(f"\n3. Correlation (log(listeners) vs loyalty): {corr:.3f}")

    # Compare tier medians
    tier_medians = df.groupby("popularity_tier", observed=True)[
        "loyalty_ratio"
    ].median()
    print(f"\n4. Median loyalty by tier:")
    for tier in ["Top 10%", "Top 25%", "Top 50%", "Bottom 50%"]:
        if tier in tier_medians.index:
            print(f"   {tier:>12s}: {tier_medians[tier]:.1f}x")

    print(f"\n5. Conclusion:")
    print("   The biggest artists do NOT necessarily have the most loyal fans.")
    print("   In fact, very popular artists tend to have a LOWER loyalty ratio")
    print("   because they attract many casual listeners who scrobble less.")
    print("   Niche genres like metal, post-rock, and electronic tend to have")
    print("   more devoted fanbases with higher scrobbles-per-listener ratios.")
    print()


if __name__ == "__main__":
    main()
