"""
Configuration for Last.fm web scrapers (pure HTML scraping, no API).
"""

# Base URL
BASE_URL = "https://www.last.fm"

# HTTP headers to mimic a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Delay between requests (seconds) — be respectful to Last.fm servers
REQUEST_DELAY = 1.0

# Seed genres to start scraping from (we scrape /tag/GENRE/artists for each)
SEED_GENRES = [
    "rock", "pop", "electronic", "hip-hop", "indie", "alternative", "metal",
    "jazz", "classical", "r&b", "folk", "punk", "soul", "blues", "country",
    "reggae", "latin", "k-pop", "ambient", "dance", "house", "techno",
    "post-punk", "new wave", "funk", "shoegaze", "dream pop", "emo",
    "trap", "grunge", "singer-songwriter", "post-rock", "psychedelic",
    "hard rock", "synth-pop", "disco", "progressive rock", "garage rock",
    "trip-hop", "downtempo", "experimental", "lo-fi", "britpop",
    "drum and bass", "dubstep", "afrobeats", "gothic", "industrial",
    "soundtrack", "noise",
]

# How many artists to collect listeners from (for user scraping)
NUM_ARTISTS_FOR_USERS = 15

# How many pages of tracks to scrape per artist (50 tracks/page)
TRACK_PAGES_PER_ARTIST = 1

# Output directory for CSV files
OUTPUT_DIR = "../data"
