#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tracker.py
----------
Reads a list of RSS feeds (from feeds.txt), looks for Nintendo Switch 2 news,
and writes any new items to the top of NEWS.md.

It stores the links it has already recorded in data/seen.json, so the same
item is never added twice.

Designed to run on its own via a scheduled GitHub Action, but you can also run
it by hand:  python tracker.py
"""

import json
import os
import datetime
import html

import feedparser  # library that reads RSS/Atom feeds. Install with: pip install feedparser


# --- Configuration -----------------------------------------------------------

# For feeds WITHOUT the "all" mode, an item is kept only if its title or summary
# contains one of these keywords (case-insensitive).
KEYWORDS = [
    "switch 2",
    "switch2",
]

# Files used by the script (paths relative to this file).
HERE = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(HERE, "feeds.txt")
SEEN_FILE = os.path.join(HERE, "data", "seen.json")
NEWS_FILE = os.path.join(HERE, "NEWS.md")


# --- Helper functions --------------------------------------------------------

def read_feeds():
    """Read feeds.txt and return a list of (url, mode) tuples.

    Each useful line is:  URL   [mode]
      - mode "all"  -> keep every post from that feed.
      - no mode     -> filter posts by KEYWORDS.
    """
    feeds = []
    with open(FEEDS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()                 # split on spaces/tabs
            url = parts[0]
            mode = parts[1].lower() if len(parts) > 1 else "filter"
            feeds.append((url, mode))
    return feeds


def load_seen():
    """Load the set of links already recorded. If missing, start empty."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    """Save the set of seen links to disk (as a sorted list)."""
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def is_relevant(entry):
    """True if the item's title or summary mentions one of the KEYWORDS."""
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    text = (title + " " + summary).lower()
    return any(word in text for word in KEYWORDS)


# --- Main program ------------------------------------------------------------

def main():
    seen = load_seen()
    new_items = []  # news items found during this run

    for url, mode in read_feeds():
        print(f"Reading feed ({mode}): {url}")
        # feedparser never raises: on failure it just returns something empty.
        feed = feedparser.parse(url)
        source = feed.feed.get("title", url)  # human-readable source name

        for entry in feed.entries:
            link = entry.get("link")
            if not link or link in seen:
                continue  # no link, or already recorded: skip it
            # In "all" mode we keep everything; otherwise filter by keywords.
            if mode != "all" and not is_relevant(entry):
                continue  # not about Switch 2

            title = html.unescape(entry.get("title", "(no title)")).strip()
            new_items.append({"title": title, "link": link, "source": source})
            seen.add(link)  # mark as seen so we never repeat it

    if not new_items:
        print("No new items.")
        return

    print(f"{len(new_items)} new item(s)!")

    # Build the block of text we will add at the TOP of the file.
    today = datetime.date.today().isoformat()
    lines = [f"## {today}", ""]
    for item in new_items:
        lines.append(f"- [{item['title']}]({item['link']}) — _{item['source']}_")
    lines.append("")  # blank separator line
    new_block = "\n".join(lines)

    # Read what was already there (or create the header if the file is missing).
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, encoding="utf-8") as f:
            previous = f.read()
    else:
        previous = ""

    header = "# Nintendo Switch 2 news (emulation & homebrew)\n\n"
    body = previous
    if body.startswith(header):
        body = body[len(header):]

    # Write: header + new items + whatever was there before.
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        f.write(header + new_block + "\n" + body)

    save_seen(seen)
    print("NEWS.md updated.")


if __name__ == "__main__":
    main()
