"""
Scraper for Last.fm musical genres (tags) — pure HTML scraping.

Strategy:
  - Use a seed list of popular genres (since /tag gives 502)
  - For each genre, scrape /tag/GENRE/artists to get top artists and count
  - Collect tags found on artist pages to discover more genres
"""

import os
import csv
from config import BASE_URL, SEED_GENRES, OUTPUT_DIR
from utils import fetch_page, polite_sleep


def scrape_genres(seed_genres=None):
    """
    Scrape genre data from Last.fm tag pages.

    Returns:
        list[dict] with keys: name, url, reach, top_artists, num_artists_tagged
    """
    if seed_genres is None:
        seed_genres = SEED_GENRES

    genres = []

    for i, genre_name in enumerate(seed_genres):
        print(f"[Genres] Scraping '{genre_name}' ({i+1}/{len(seed_genres)})...")
        url = f"{BASE_URL}/tag/{genre_name.replace(' ', '+')}/artists"
        soup = fetch_page(url)

        if not soup:
            polite_sleep()
            continue

        # Extract artist names from the tag artist page
        artist_links = soup.select("h3.big-artist-list-title a")
        artist_names = [a.get_text(strip=True) for a in artist_links]

        # Count all link-block-target as rough "reach" indicator
        all_links = soup.select(".link-block-target")

        genres.append({
            "name": genre_name,
            "url": f"{BASE_URL}/tag/{genre_name.replace(' ', '+')}",
            "reach": len(all_links),
            "top_artists": "; ".join(artist_names[:10]),
            "num_artists_tagged": len(artist_names),
        })

        print(f"  Found {len(artist_names)} artists for '{genre_name}'")
        polite_sleep()

    return genres


def save_genres_csv(genres, filename="genres.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["name", "url", "reach", "top_artists", "num_artists_tagged"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(genres)

    print(f"\n[Genres] Saved {len(genres)} genres -> {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Last.fm Genre Scraper (HTML)")
    print("=" * 60)
    genres = scrape_genres()
    save_genres_csv(genres)
    print("Done!")
