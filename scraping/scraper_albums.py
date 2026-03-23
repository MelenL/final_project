"""
Scraper for Last.fm albums — pure HTML scraping.

Strategy:
  - For each artist, scrape /music/ARTIST/+albums
  - Extract album names from .link-block-target elements
  - Visit individual album pages for listener/scrobble stats

Source pages:
  - https://www.last.fm/music/Radiohead/+albums
  - https://www.last.fm/music/Radiohead/OK+Computer (individual album)
"""

import os
import csv
from config import BASE_URL, OUTPUT_DIR
from utils import fetch_page, parse_abbr_number, polite_sleep


def scrape_top_albums(artist_list, max_albums_per_artist=3):
    """
    Scrape top albums for a list of artists.

    Args:
        artist_list: list of dicts with 'name' and 'url' keys (from scraper_artists)
        max_albums_per_artist: how many albums per artist

    Returns:
        list[dict] with keys: name, artist, listeners, play_count, url, tags, num_tracks
    """
    albums = []
    seen = set()

    for i, artist in enumerate(artist_list):
        artist_name = artist["name"]
        # Build the albums URL from artist URL
        albums_url = artist["url"].rstrip("/") + "/+albums"
        print(f"[Albums] {artist_name} ({i+1}/{len(artist_list)})...")

        soup = fetch_page(albums_url)
        if not soup:
            polite_sleep()
            continue

        # .link-block-target gives album links
        # Filter to only those that are actual album links (contain /music/ARTIST/ALBUM)
        links = soup.select(".link-block-target")
        count = 0
        for link in links:
            href = link.get("href", "")
            name = link.get_text(strip=True)
            # Album hrefs look like /music/Radiohead/OK+Computer
            # Skip if it's an artist link, user link, or other
            if not href or "/music/" not in href or name == "" or "/_/" in href:
                continue
            # Must be a subpath of the artist (not just /music/AnotherArtist)
            if href.count("/") < 3:
                continue

            full_url = BASE_URL + href if href.startswith("/") else href
            key = (name.lower(), artist_name.lower())
            if key in seen:
                continue
            seen.add(key)

            albums.append({
                "name": name,
                "artist": artist_name,
                "listeners": 0,
                "play_count": 0,
                "url": full_url,
                "tags": artist.get("top_tags", ""),
                "num_tracks": 0,
            })
            count += 1
            if count >= max_albums_per_artist:
                break

        print(f"  Found {count} albums")
        polite_sleep()

    # Enrich a subset of albums with listener stats from individual pages
    print(f"\n[Albums] Enriching {len(albums)} albums with stats...")
    for i, album in enumerate(albums):
        _enrich_album(album)
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(albums)}")
        polite_sleep()

    return albums


def _enrich_album(album):
    """
    Visit the individual album page for listeners, scrobbles, track count.
    Uses same abbr.intabbr pattern as artist pages.
    """
    soup = fetch_page(album["url"])
    if not soup:
        return

    # Listeners and scrobbles
    abbrs = soup.select("abbr.intabbr")
    if len(abbrs) >= 2:
        album["listeners"] = parse_abbr_number(abbrs[0].get_text(strip=True))
        album["play_count"] = parse_abbr_number(abbrs[1].get_text(strip=True))
    elif len(abbrs) == 1:
        album["listeners"] = parse_abbr_number(abbrs[0].get_text(strip=True))

    # Tags (may override the artist tags with album-specific ones)
    tag_elems = soup.select(".catalogue-tags .tag")
    if tag_elems:
        album["tags"] = "; ".join(t.get_text(strip=True) for t in tag_elems[:5])

    # Count tracks in the tracklist
    track_rows = soup.select(".chartlist-row")
    if track_rows:
        album["num_tracks"] = len(track_rows)


def save_albums_csv(albums, filename="albums.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["name", "artist", "listeners", "play_count", "url", "tags",
                  "num_tracks"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(albums)

    print(f"\n[Albums] Saved {len(albums)} albums -> {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Last.fm Album Scraper (HTML)")
    print("=" * 60)
    # Quick test: scrape albums for a few artists
    from scraper_artists import scrape_top_artists
    artists = scrape_top_artists(seed_genres=["rock", "pop"], max_artists=10)
    albums = scrape_top_albums(artists)
    save_albums_csv(albums)
    print("Done!")
