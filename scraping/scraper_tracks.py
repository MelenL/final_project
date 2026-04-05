"""
Scraper for Last.fm tracks (songs) — pure HTML scraping.

Strategy:
  - For each artist, scrape /music/ARTIST/+tracks
  - Extract track name (.chartlist-name a) and listeners (.chartlist-count-bar-value)
  - Visit individual track pages for duration

Source pages:
  - https://www.last.fm/music/Radiohead/+tracks
  - https://www.last.fm/music/Radiohead/_/Creep (individual track)
"""

import os
import csv
from config import BASE_URL, OUTPUT_DIR
from utils import (
    completeness_ratio,
    extract_duration_seconds,
    extract_listener_playcount,
    extract_tag_list,
    fetch_page,
    parse_count_text,
    polite_sleep,
)


def scrape_top_tracks(artist_list, max_tracks_per_artist=5):
    """
    Scrape top tracks for a list of artists.

    Two-pass strategy:
      Pass 1 — /music/ARTIST/+tracks : collect track names and listener counts.
                                        Duration is not available on this page.
      Pass 2 — /music/ARTIST/_/TRACK : visit each track page for duration,
                                        play count, and track-specific tags.

    Args:
        artist_list: list of dicts with 'name', 'url', 'top_tags'
        max_tracks_per_artist: how many tracks per artist

    Returns:
        list[dict] with keys:
          name, artist, duration_seconds, listeners, play_count, url, tags, data_quality
    """
    tracks = []

    # Pass 1: collect track stubs (name, URL, listener count) from the listing page
    for i, artist in enumerate(artist_list):
        artist_name = artist["name"]
        tracks_url = artist["url"].rstrip("/") + "/+tracks"
        print(f"[Tracks] {artist_name} ({i+1}/{len(artist_list)})...")

        soup = fetch_page(tracks_url)
        if not soup:
            polite_sleep()
            continue

        rows = soup.select(".chartlist-row")
        count = 0
        for row in rows[:max_tracks_per_artist]:
            track = _parse_track_row(row, artist_name, artist.get("top_tags", ""))
            if track:
                tracks.append(track)
                count += 1

        print(f"  Found {count} tracks")
        polite_sleep()

    # Pass 2: visit each track page to fill in duration, play count, and tags
    print(f"\n[Tracks] Fetching duration for {len(tracks)} tracks...")
    for i, track in enumerate(tracks):
        _enrich_track_duration(track)
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(tracks)}")
        polite_sleep()

    return tracks


def _parse_track_row(row, artist_name, artist_tags):
    """
    Parse a single .chartlist-row for track data.
    - .chartlist-name a: track name + URL
    - .chartlist-count-bar-value: '4,031,390listeners'
    """
    name_elem = row.select_one(".chartlist-name a")
    if not name_elem:
        return None

    name = name_elem.get_text(strip=True)
    href = name_elem.get("href", "")
    url = BASE_URL + href if href.startswith("/") else href

    # Listener count
    count_elem = row.select_one(".chartlist-count-bar-value")
    listeners = parse_count_text(count_elem.get_text(strip=True)) if count_elem else 0

    return {
        "name": name,
        "artist": artist_name,
        "duration_seconds": 0,  # Will be filled by enrichment
        "listeners": listeners,
        "play_count": 0,
        "url": url,
        "tags": artist_tags,
        "data_quality": 0.0,
    }


def _enrich_track_duration(track):
    """
    Visit the individual track page to find the duration.
    The track page may have duration in catalogue-metadata or similar elements.
    Also collects play_count and track-specific tags.
    """
    soup = fetch_page(track["url"])
    if not soup:
        return

    track["duration_seconds"] = extract_duration_seconds(soup)

    listeners, play_count = extract_listener_playcount(soup)
    track["listeners"] = max(track["listeners"], listeners)
    track["play_count"] = play_count

    tags = extract_tag_list(soup, limit=10)
    if tags:
        track["tags"] = "; ".join(tags)

    track["data_quality"] = completeness_ratio(
        [track["duration_seconds"], track["listeners"], track["play_count"], track["tags"]]
    )


def save_tracks_csv(tracks, filename="tracks.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = [
        "name",
        "artist",
        "duration_seconds",
        "listeners",
        "play_count",
        "url",
        "tags",
        "data_quality",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tracks)

    print(f"\n[Tracks] Saved {len(tracks)} tracks -> {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Last.fm Track Scraper (HTML)")
    print("=" * 60)
    from scraper_artists import scrape_top_artists
    artists = scrape_top_artists(seed_genres=["rock"], max_artists=5)
    tracks = scrape_top_tracks(artists)
    save_tracks_csv(tracks)
    print("Done!")
