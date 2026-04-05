"""
Shared utilities for Last.fm HTML scrapers.
"""

import re
import time

import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_DELAY


# CSS selectors for genre tags, tried in order (fallbacks for layout variations)
TAG_SELECTORS = [
    ".catalogue-tags .tag",   # standard tag block on artist/album/track pages
    ".tags-list a.tag",       # alternative tag list layout
    "a[href^='/tag/']",       # any link pointing to a tag page
]

# CSS selectors for listener/scrobble counts, tried in order
STAT_SELECTORS = [
    "abbr.intabbr",                # primary: abbreviated numbers like "8.2M"
    ".header-metadata-tnew-count", # newer header layout
    ".header-metadata-value",      # generic header metadata
    ".catalogue-metadata-value",   # catalogue metadata (album/track pages)
]


def normalize_space(text):
    """Collapse repeated whitespace into single spaces."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def fetch_page(url, retries=3, backoff=1.5):
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None if the request fails after retries.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(REQUEST_DELAY * backoff * attempt)

    print(f"  Error fetching {url}: {last_error}")
    return None


def parse_abbr_number(text):
    """
    Parse abbreviated numbers like '8.2M', '1.36B', '342K', '12,345'.
    Returns an integer.
    """
    if not text:
        return 0

    cleaned = normalize_space(text).replace(",", "")  # remove thousands separators
    match = re.search(r"([\d.]+)\s*([KMBkmb])?", cleaned)  # capture number + optional suffix
    if not match:
        return 0

    number = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return int(number * multipliers.get(suffix, 1))


def parse_count_text(text):
    """
    Parse count text like '4,031,390listeners' or '285scrobbles'.
    Extracts the numeric part.
    """
    if not text:
        return 0
    digits = re.sub(r"[^\d]", "", str(text))
    return int(digits) if digits else 0


def dedupe_preserve_order(values):
    """Return values without duplicates while preserving order."""
    seen = set()
    unique = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def extract_tag_list(soup, limit=10):
    """
    Extract tags using several fallbacks because page layouts vary.
    """
    tags = []
    for selector in TAG_SELECTORS:
        for tag_elem in soup.select(selector):
            tag_text = normalize_space(tag_elem.get_text(" ", strip=True)).lower()
            if tag_text:
                tags.append(tag_text)

    return dedupe_preserve_order(tags)[:limit]


def _find_labelled_number(text, labels):
    """
    Find numbers attached to labels such as '8.2M listeners' in page text.
    """
    for label in labels:
        match = re.search(
            rf"([\d.,]+(?:\s*[KMBkmb])?)\s*{label}",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            value = parse_abbr_number(match.group(1))
            if value > 0:
                return value
    return 0


def extract_listener_playcount(soup):
    """
    Extract listeners and play count with multiple selector and text fallbacks.
    """
    values = []
    for selector in STAT_SELECTORS:
        for elem in soup.select(selector):
            value = parse_abbr_number(elem.get_text(" ", strip=True))
            if value > 0:
                values.append(value)

    values = dedupe_preserve_order(values)
    if len(values) >= 2:
        return values[0], values[1]
    if len(values) == 1:
        return values[0], 0

    page_text = normalize_space(soup.get_text(" ", strip=True))
    listeners = _find_labelled_number(page_text, ["listeners?", "listener"])
    play_count = _find_labelled_number(page_text, ["scrobbles?", "plays?", "play count"])
    return listeners, play_count


def _match_duration_candidate(text):
    """
    Convert a duration candidate string to seconds.

    Four formats tried in order:
      1. MM:SS          — standard clock display  (e.g. "4:35")
      2. X min Y sec    — written-out English      (e.g. "4 minutes 35 seconds")
      3. ISO 8601       — JSON-LD structured data  (e.g. "PT4M35S")
      4. Milliseconds   — raw integer in scripts   (e.g. 275000 → 275 s)
    """
    if not text:
        return 0

    normalized = normalize_space(text).lower()

    match = re.search(r"\b(\d{1,2}):(\d{2})\b", normalized)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))

    match = re.search(r"\b(\d+)\s*min(?:ute)?s?\s*(\d+)\s*sec(?:ond)?s?\b", normalized)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))

    match = re.search(r'"duration"\s*:\s*"PT(?:(\d+)M)?(?:(\d+)S)?"', normalized)
    if match:
        return int(match.group(1) or 0) * 60 + int(match.group(2) or 0)

    match = re.search(r'"duration"\s*:\s*(\d{5,7})', normalized)  # milliseconds
    if match:
        return int(match.group(1)) // 1000

    return 0


def extract_duration_seconds(soup):
    """
    Extract track duration from visible metadata or embedded page text.

    Builds a list of candidate strings from most-specific to least-specific,
    then returns the first one that parses to a plausible duration (10 s – 1 h).
    """
    candidates = []

    # Structured metadata elements (most reliable sources)
    for selector in [
        ".catalogue-metadata li",
        ".catalogue-metadata-description",
        ".header-metadata-item",
        "meta[itemprop='duration']",  # <meta> carries value in 'content' attribute
    ]:
        for elem in soup.select(selector):
            content = elem.get("content") if elem.has_attr("content") else ""
            if content:
                candidates.append(content)
            candidates.append(elem.get_text(" ", strip=True))

    # Inline scripts may contain a JSON "duration" field
    for script in soup.select("script[type='application/ld+json'], script"):
        script_text = script.string or script.get_text(" ", strip=True)
        if "duration" in script_text.lower():
            candidates.append(script_text)

    candidates.append(soup.get_text(" ", strip=True))  # full page text as last resort

    for candidate in candidates:
        duration = _match_duration_candidate(candidate)
        if 10 <= duration <= 3600:
            return duration

    return 0


def extract_year(text):
    """Extract a plausible year from a text block."""
    match = re.search(r"\b(19\d{2}|20\d{2})\b", str(text))
    return int(match.group(1)) if match else 0


def completeness_ratio(values):
    """
    Compute the share of populated values among a list of fields.
    """
    if not values:
        return 0.0

    populated = 0
    for value in values:
        if isinstance(value, str):
            populated += int(bool(value.strip()))
        else:
            populated += int(bool(value))
    return round(populated / len(values), 3)


def polite_sleep():
    """Sleep between requests to be respectful."""
    time.sleep(REQUEST_DELAY)
