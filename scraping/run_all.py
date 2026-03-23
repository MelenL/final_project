"""
Master script to run all Last.fm HTML scrapers.

This collects data from Last.fm using pure web scraping (requests + BeautifulSoup).
No API key needed.

Usage:
    cd scraping/
    python run_all.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR
from scraper_genres import scrape_genres, save_genres_csv
from scraper_artists import scrape_top_artists, save_artists_csv
from scraper_albums import scrape_top_albums, save_albums_csv
from scraper_tracks import scrape_top_tracks, save_tracks_csv
from scraper_users import scrape_users, save_users_csv


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start_time = time.time()

    print("=" * 70)
    print("LAST.FM DATA COLLECTION — Pure Web Scraping")
    print("Programming for Data Science - Final Project")
    print("=" * 70)
    print()

    # --- 1. Genres ---
    print("-" * 50)
    print("STEP 1/5: Scraping Musical Genres")
    print("-" * 50)
    genres = scrape_genres()
    save_genres_csv(genres)
    print()

    # --- 2. Artists ---
    print("-" * 50)
    print("STEP 2/5: Scraping Top Artists")
    print("-" * 50)
    artists = scrape_top_artists(max_artists=200)
    save_artists_csv(artists)
    print()

    # --- 3. Albums ---
    print("-" * 50)
    print("STEP 3/5: Scraping Top Albums")
    print("-" * 50)
    albums = scrape_top_albums(artists, max_albums_per_artist=3)
    save_albums_csv(albums)
    print()

    # --- 4. Tracks ---
    print("-" * 50)
    print("STEP 4/5: Scraping Top Tracks")
    print("-" * 50)
    tracks = scrape_top_tracks(artists, max_tracks_per_artist=5)
    save_tracks_csv(tracks)
    print()

    # --- 5. Users ---
    print("-" * 50)
    print("STEP 5/5: Scraping User Profiles")
    print("-" * 50)
    users = scrape_users(artists)
    save_users_csv(users)
    print()

    # --- Summary ---
    elapsed = time.time() - start_time
    print("=" * 70)
    print("SCRAPING COMPLETE!")
    print(f"  Genres  : {len(genres)}")
    print(f"  Artists : {len(artists)}")
    print(f"  Albums  : {len(albums)}")
    print(f"  Tracks  : {len(tracks)}")
    print(f"  Users   : {len(users)}")
    print(f"  Time    : {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Output  : {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
