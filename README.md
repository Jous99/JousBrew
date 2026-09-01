# JousBrew — Switch 2 news tracker

A repository that **updates itself**: several times a day it checks a few sources
for Nintendo Switch 2 emulation & homebrew news and, whenever something new shows
up, it records it in [`NEWS.md`](NEWS.md) with an automatic commit. You don't need
to keep anything running — GitHub does all the work for free (GitHub Actions).

## How it works (4 pieces)

1. **`feeds.txt`** — the list of RSS sources to watch (Wayayeo, Wololo, Nintendo
   Life, Reddit searches...). Add or remove any you like.
2. **`tracker.py`** — the program: reads the feeds, keeps what's relevant, avoids
   duplicates (it remembers links in `data/seen.json`) and writes new items at the
   very top of `NEWS.md`.
3. **`.github/workflows/tracker.yml`** — the "clock": tells GitHub to run the
   program on a schedule and commit the changes.
4. **`NEWS.md`** — the result, which fills up on its own.

## Automatic updates

The workflow runs on its own in three ways:

- **On a schedule** — every 6 hours (the `cron` line in the workflow).
- **On push** — whenever you push to `main`.
- **On demand** — the *Run workflow* button in the Actions tab.

Each run commits any new items back to the repo automatically, so the history of
`NEWS.md` is your feed of updates. Change how often it runs by editing the `cron`
line (e.g. `0 */3 * * *` = every 3 hours).

## Setup (step by step)

1. Create a GitHub account at [github.com](https://github.com) if you don't have one.
2. Create a new repository (e.g. `JousBrew`). Public or private, your call.
3. Upload these files to the repository. Two ways:
   - **Easy (web):** *Add file → Upload files* and drag everything in. Heads-up:
     the `.github` folder sometimes won't upload by dragging because it starts with
     a dot. If that happens, create it by hand with *Add file → Create new file*
     and type the path `.github/workflows/tracker.yml`.
   - **With git (terminal):**
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/JousBrew.git
     git push -u origin main
     ```
4. In the repository, go to **Settings → Actions → General**, scroll to
   *Workflow permissions* and select **"Read and write permissions"**, then *Save*.
   This is what lets the bot commit.
5. Go to the **Actions** tab, pick *"JousBrew Tracker"* and press **"Run workflow"**
   to try it right now instead of waiting.

## Run it locally (optional)

```bash
pip install -r requirements.txt
python tracker.py
```

## Tweaks

- **Sources:** edit `feeds.txt`. One URL per line; `#` lines are comments. Add
  `all` after a URL to keep **every** post from that feed (good for small,
  on-topic sites like Wayayeo); without `all`, it only keeps posts that mention
  the keywords.
  Tip: almost any WordPress site exposes its feed at `/feed/` (e.g.
  `https://wayayeo.org/feed/`). That's more reliable than scraping the HTML.
- **What counts as relevant:** the `KEYWORDS` list in `tracker.py`. Add e.g.
  `"atmosphere"` or `"eden"` to catch those too.
- **How often it runs:** the `cron` line in the workflow.

## Notes

- If a feed stops working, the script just skips it; nothing breaks.
- The first run may pick up several items at once (the recent ones from each
  feed). After that you'll only see what's new.
