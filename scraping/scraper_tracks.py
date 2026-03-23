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
import re
import csv
from config import BASE_URL, OUTPUT_DIR
from utils import fetch_page, parse_count_text, polite_sleep


def scrape_top_tracks(artist_list, max_tracks_per_artist=5):
    """
    Scrape top tracks for a list of artists.

    Args:
        artist_list: list of dicts with 'name', 'url', 'top_tags'
        max_tracks_per_artist: how many tracks per artist

    Returns:
        list[dict] with keys:
          name, artist, duration_seconds, listeners, play_count, url, tags
    """
    tracks = []

    for i, artist in enumerate(artist_list):
        artist_name = artist["name"]
        tracks_url = artist["url"].rstrip("/") + "/+tracks"
        print(f"[Tracks] {artist_name} ({i+1}/{len(artist_list)})...")

        soup = fetch_page(tracks_url)
        if not soup:
            polite_sleep()
            continue

        # Each track is a .chartlist-row
        rows = soup.select(".chartlist-row")
        count = 0
        for row in rows[:max_tracks_per_artist]:
            track = _parse_track_row(row, artist_name, artist.get("top_tags", ""))
            if track:
                tracks.append(track)
                count += 1

        print(f"  Found {count} tracks")
        polite_sleep()

    # Enrich tracks with duration from individual track pages
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

    # Look for duration in metadata sections
    # Try catalogue-metadata items
    meta_items = soup.select(".catalogue-metadata li, .catalogue-metadata-description")
    for item in meta_items:
        text = item.get_text(strip=True).lower()
        # Duration patterns: "3:45", "4 min 2 sec", "225000" (ms)
        time_match = re.search(r"(\d{1,2}):(\d{2})", text)
        if time_match:
            mins = int(time_match.group(1))
            secs = int(time_match.group(2))
            track["duration_seconds"] = mins * 60 + secs
            break

    # Get scrobbles (play_count) from header stats
    abbrs = soup.select("abbr.intabbr")
    if len(abbrs) >= 2:
        # For tracks: first = listeners, second = scrobbles
        from utils import parse_abbr_number
        track["listeners"] = max(track["listeners"],
                                  parse_abbr_number(abbrs[0].get_text(strip=True)))
        track["play_count"] = parse_abbr_number(abbrs[1].get_text(strip=True))

    # Track-specific tags
    tag_elems = soup.select(".catalogue-tags .tag")
    if tag_elems:
        track["tags"] = "; ".join(t.get_text(strip=True) for t in tag_elems[:5])


def save_tracks_csv(tracks, filename="tracks.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["name", "artist", "duration_seconds", "listeners",
                  "play_count", "url", "tags"]
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
