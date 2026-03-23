"""
Shared utilities for Last.fm HTML scrapers.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from config import BASE_URL, HEADERS, REQUEST_DELAY


def fetch_page(url):
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None if the request fails.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None


def parse_abbr_number(text):
    """
    Parse abbreviated numbers like '8.2M', '1.36B', '342K', '12,345'.
    Returns an integer.
    """
    if not text:
        return 0
    text = text.strip().replace(",", "")
    # Match patterns like 8.2M, 1.36B, 342K
    match = re.match(r"([\d.]+)\s*([KMBkmb])?", text)
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
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def polite_sleep():
    """Sleep between requests to be respectful."""
    time.sleep(REQUEST_DELAY)
