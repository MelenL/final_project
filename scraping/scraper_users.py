"""
Scraper for Last.fm user profiles — pure HTML scraping.

Strategy:
  1. Visit /music/ARTIST/+listeners to discover usernames
  2. Visit /user/USERNAME to scrape profile data

Source pages:
  - https://www.last.fm/music/Radiohead/+listeners
  - https://www.last.fm/user/RJ
"""

import os
import re
import csv
from config import BASE_URL, NUM_ARTISTS_FOR_USERS, OUTPUT_DIR
from utils import fetch_page, parse_count_text, polite_sleep


def scrape_users(artist_list):
    """
    Scrape user profiles from Last.fm.

    Args:
        artist_list: list of artist dicts (with 'name' and 'url')

    Returns:
        list[dict] with keys:
          username, country, age, scrobble_count, url,
          top_genres, playlists_count, registered_year
    """
    # Step 1: Collect usernames from artist listener pages
    usernames = set()
    for artist in artist_list[:NUM_ARTISTS_FOR_USERS]:
        artist_name = artist["name"]
        listeners_url = artist["url"].rstrip("/") + "/+listeners"
        print(f"[Users] Getting listeners of: {artist_name}")

        soup = fetch_page(listeners_url)
        if not soup:
            polite_sleep()
            continue

        # .link-block-target with /user/ in href
        links = soup.select(".link-block-target")
        for link in links:
            href = link.get("href", "")
            match = re.search(r"^/user/([^/]+)$", href)
            if match:
                usernames.add(match.group(1))

        print(f"  Total unique users: {len(usernames)}")
        polite_sleep()

    print(f"\n[Users] Collected {len(usernames)} unique usernames. "
          f"Scraping profiles...")

    # Step 2: Visit each user profile
    users = []
    for i, username in enumerate(usernames):
        user = _scrape_user_profile(username)
        if user:
            users.append(user)
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i + 1}/{len(usernames)}")
        polite_sleep()

    return users


def _scrape_user_profile(username):
    """
    Scrape a user's profile page.

    HTML structure (from inspection):
      - li.header-metadata-item: 'Scrobbles150,446', 'Artists12,750'
      - .header-scrobble-since: '• scrobbling since 20 Nov 2002'
      - .header-title-secondary: 'Richard Jones• scrobbling since ...'
    """
    url = f"{BASE_URL}/user/{username}"
    soup = fetch_page(url)
    if not soup:
        return None

    user = {
        "username": username,
        "country": "",
        "age": 0,
        "scrobble_count": 0,
        "url": url,
        "top_genres": "",
        "playlists_count": 0,
        "registered_year": 0,
    }

    # Scrobble count from li.header-metadata-item
    metadata_items = soup.select("li.header-metadata-item")
    for item in metadata_items:
        text = item.get_text(strip=True).lower()
        if "scrobble" in text:
            user["scrobble_count"] = parse_count_text(text)

    # Registration year from .header-scrobble-since
    since_elem = soup.select_one(".header-scrobble-since")
    if since_elem:
        text = since_elem.get_text(strip=True)
        year_match = re.search(r"(20\d{2}|19\d{2})", text)
        if year_match:
            user["registered_year"] = int(year_match.group(1))

    # Name / country from .header-title-secondary
    # Format: "Richard Jones• scrobbling since..." or just "• scrobbling since..."
    secondary = soup.select_one(".header-title-secondary")
    if secondary:
        text = secondary.get_text(strip=True)
        # Extract the part before "scrobbling"
        parts = re.split(r"[•·]", text)
        if parts and parts[0].strip():
            # This could be name, or name + location
            user_info = parts[0].strip()
            # Some profiles show "Name, Country" or just "Name"
            if "," in user_info:
                name_parts = user_info.rsplit(",", 1)
                user["country"] = name_parts[-1].strip()

    # Try to find genre preferences from the user page
    # User pages have top artists sections with .grid-items
    # We'll extract artist tags as a proxy for user genres
    tag_links = soup.select(".catalogue-tags .tag, .tags-list a.tag")
    if tag_links:
        user["top_genres"] = "; ".join(
            t.get_text(strip=True) for t in tag_links[:5]
        )

    return user


def save_users_csv(users, filename="users.csv"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["username", "country", "age", "scrobble_count", "url",
                  "top_genres", "playlists_count", "registered_year"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

    print(f"\n[Users] Saved {len(users)} users -> {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Last.fm User Scraper (HTML)")
    print("=" * 60)
    from scraper_artists import scrape_top_artists
    artists = scrape_top_artists(seed_genres=["rock"], max_artists=5)
    users = scrape_users(artists)
    save_users_csv(users)
    print("Done!")
