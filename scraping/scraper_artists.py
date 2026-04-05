"""
Scraper for Last.fm top artists — pure HTML scraping.

Strategy:
  1. Collect artist names from genre tag pages (/tag/GENRE/artists)
  2. Visit each artist's page (/music/ARTIST) to get:
     - Listeners and scrobble count (abbr.intabbr)
     - Genre tags (.catalogue-tags .tag)

Source pages:
  - https://www.last.fm/tag/rock/artists
  - https://www.last.fm/music/Radiohead
"""

import os
import csv
from config import BASE_URL, SEED_GENRES, OUTPUT_DIR
from utils import (
    completeness_ratio,
    extract_listener_playcount,
    extract_tag_list,
    fetch_page,
    polite_sleep,
)


def scrape_top_artists(seed_genres=None, max_artists=200):
    """
    Collect artists from genre tag pages, then enrich from individual
    artist pages.

    Two-pass strategy:
      Pass 1 — /tag/GENRE/artists : collect artist names and URLs (no stats yet).
      Pass 2 — /music/ARTIST      : visit each page for listeners, play count, tags.

    Args:
        seed_genres: list of genre names to scrape artists from
        max_artists: maximum number of unique artists to collect

    Returns:
        list[dict] with keys:
          name, listeners, play_count, url, top_tags, tag_count, data_quality
    """
    if seed_genres is None:
        seed_genres = SEED_GENRES

    # Pass 1: collect artist names and URLs from genre tag pages
    seen = set()       # prevents the same artist from being added twice
    artist_stubs = []  # lightweight records (name + URL only)

    for genre_name in seed_genres:
        url = f"{BASE_URL}/tag/{genre_name.replace(' ', '+')}/artists"
        print(f"[Artists] Collecting from /tag/{genre_name}/artists ...")
        soup = fetch_page(url)

        if not soup:
            polite_sleep()
            continue

        links = soup.select("h3.big-artist-list-title a")
        count = 0
        for link in links:
            name = link.get_text(strip=True)
            href = link.get("href", "")
            if name and name not in seen:
                seen.add(name)
                artist_stubs.append({
                    "name": name,
                    "url": BASE_URL + href if href.startswith("/") else href,
                })
                count += 1

        print(f"  +{count} new artists (total unique: {len(artist_stubs)})")
        polite_sleep()

        if len(artist_stubs) >= max_artists:
            break

    artist_stubs = artist_stubs[:max_artists]
    print(f"\n[Artists] Collected {len(artist_stubs)} unique artists. "
          f"Enriching from individual pages...")

    # Pass 2: visit each artist page to get listeners, play count, and tags
    artists = []
    for i, stub in enumerate(artist_stubs):
        artist = _enrich_artist(stub)
        artists.append(artist)
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(artist_stubs)}")
        polite_sleep()

    return artists


def _enrich_artist(stub):
    """
    Visit /music/ARTIST to extract listeners, play_count, and tags.

    HTML structure (from inspection):
      - abbr.intabbr: ['8.2M', '1.36B'] → [listeners, scrobbles]
      - .catalogue-tags .tag: ['alternative', 'rock', ...]
    """
    artist = {
        "name": stub["name"],
        "listeners": 0,
        "play_count": 0,
        "url": stub["url"],
        "top_tags": "",
        "tag_count": 0,
        "data_quality": 0.0,
    }

    soup = fetch_page(stub["url"])
    if not soup:
        return artist

    artist["listeners"], artist["play_count"] = extract_listener_playcount(soup)

    tags = extract_tag_list(soup, limit=10)
    artist["top_tags"] = "; ".join(tags)
    artist["tag_count"] = len(tags)
    artist["data_quality"] = completeness_ratio(
        [artist["listeners"], artist["play_count"], artist["top_tags"]]
    )

    return artist


def save_artists_csv(artists, filename="artists.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "name",
        "listeners",
        "play_count",
        "url",
        "top_tags",
        "tag_count",
        "data_quality",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(artists)

    print(f"\n[Artists] Saved {len(artists)} artists -> {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Last.fm Artist Scraper (HTML)")
    print("=" * 60)
    artists = scrape_top_artists()
    save_artists_csv(artists)
    print("Done!")
