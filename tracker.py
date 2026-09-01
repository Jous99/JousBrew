#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tracker.py
----------
Reads a list of RSS feeds (from feeds.txt), looks for Nintendo Switch 2
piracy / homebrew / hacking / emulation news, and writes any new items to the
top of NEWS.md.

An item is kept only when it mentions BOTH:
  1) the console  -> one of CONSOLE_KEYWORDS  ("switch 2")
  2) the topic    -> one of TOPIC_KEYWORDS    (homebrew, exploit, emulator...)

It stores the links it has already recorded in data/seen.json, so the same
item is never added twice.

Designed to run on its own via a scheduled Action, but you can also run it by
hand:  python tracker.py
"""

import json
import os
import datetime
import html

import feedparser  # library that reads RSS/Atom feeds. Install with: pip install feedparser


# --- Configuration -----------------------------------------------------------

# 1) The item must be about the Switch 2.
CONSOLE_KEYWORDS = [
    "switch 2",
    "switch2",
]

# 2) AND it must be about piracy / homebrew / hacking / emulation.
#    All lowercase. Substring match, so "hack" also catches "hacked"/"hacking".
TOPIC_KEYWORDS = [
    "homebrew",
    "piracy", "pirate", "pirated", "pirateo", "pirater",   # en + es
    "jailbreak",
    "hack",          # hack, hacked, hacking
    "exploit",
    "modchip",
    "modding",
    "custom firmware", "cfw",
    "emulator", "emulation", "emulate",
    "atmosphere", "hekate",
    "prod.keys", "bootrom", "rcm",
    "picofly", "hwfly", "mig flash", "mig switch",
    "warez", "undub",
]

# Files used by the script (paths relative to this file).
HERE = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(HERE, "feeds.txt")
SEEN_FILE = os.path.join(HERE, "data", "seen.json")
NEWS_FILE = os.path.join(HERE, "NEWS.md")


# --- Helper functions --------------------------------------------------------

def read_feeds():
    """Read feeds.txt and return the list of URLs (ignoring comments/blanks)."""
    urls = []
    with open(FEEDS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line.split()[0])  # take just the URL, ignore extras
    return urls


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
    """True only if the item mentions Switch 2 AND a piracy/homebrew topic."""
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    text = (title + " " + summary).lower()

    about_switch2 = any(word in text for word in CONSOLE_KEYWORDS)
    about_topic = any(word in text for word in TOPIC_KEYWORDS)
    return about_switch2 and about_topic


# --- Main program ------------------------------------------------------------

def main():
    seen = load_seen()
    new_items = []  # news items found during this run

    for url in read_feeds():
        print(f"Reading feed: {url}")
        # feedparser never raises: on failure it just returns something empty.
        feed = feedparser.parse(url)
        source = feed.feed.get("title", url)  # human-readable source name

        for entry in feed.entries:
            link = entry.get("link")
            if not link or link in seen:
                continue  # no link, or already recorded: skip it
            if not is_relevant(entry):
                continue  # not Switch 2 piracy/homebrew: skip it

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
