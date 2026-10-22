# Humanoid News (humanoidbeat.com)

Static humanoid-robotics news site, owned and operated by Joshua Israel Ventures LLC.
GitHub Pages serves `docs/` from `main`. `docs/` is **generated** — never edit it by hand.

```
build.py                 generator (python3 build.py; needs Pillow + cairosvg)
content/articles.json    all articles (the only content file the daily routine edits)
src-img/                 source photos (originals; only the processed versions are published)
assets/                  style.css, app.js (copied to docs/assets)
images.md                auto-generated: source + licence per image
docs/                    published site (built output, plus CNAME)
```

Setup once: `python3 -m venv v && v/bin/pip install pillow cairosvg && v/bin/python build.py`

## Config (top of build.py)
- `SITE_URL` – the one place for the domain (currently `https://humanoidbeat.com`, no trailing slash). `docs/CNAME` must match.
- `EMAIL` – public contact address (still a placeholder: `hello@example.com`).
- `CF_BEACON_TOKEN` – Cloudflare Web Analytics token. Set the constant or the env var `CF_BEACON_TOKEN=xxxx python3 build.py`. When set, every page gets the beacon script before `</body>` and the Privacy page mentions it. Empty = no analytics.
- `INDEXNOW_KEY` – matches the key file in `docs/`.

## Daily routine

### 1. Add a news article
Append an object to `content/articles.json` (newest order is handled automatically):
```json
{"slug":"short-kebab-slug","date":"2026-10-23","cat":"Figure",
 "title":"...","summary":"One-sentence answer, ≤160 chars.",
 "body":["<strong>Short answer:</strong> ...","Paragraph 2 ...","..."],
 "sources":[{"title":"Publisher: headline","url":"https://..."}],
 "image":{ ... see below ... }}
```
Rules: answer-first, original wording, every fact traceable to a listed source, no invented quotes. Body strings may contain `<strong>`, `<a>`, `<em>`.

### 2. Add a "why it's trending" post
Same as an article plus two fields:
```json
"kind":"trending",
"why":["Bullet: what happened and who is driving attention (cite a source)","Bullet: what to watch next"]
```
It gets a "Trending" tag, a highlighted "Why it's trending" box on the page, and appears in the "Why it's trending" section on the home page (latest 4). Bullets must be verifiable from `sources`; don't invent metrics (views, searches) you haven't seen.

### 3. Images (every article should have one; `image` object)
- **Generated illustration** (always allowed, no licence risk):
  `"image":{"art":"chip|factory|hazard","accent":"#22d3ee","alt":"Describe the picture"}`
- **Open-licence photo** (CC0 / public domain preferred; CC BY / BY-SA only with credit shown): find on Wikimedia Commons, check the file's licence box, download the original into `src-img/`, then:
  `"image":{"src":"src-img/name.jpg","crop":[left,top,width],"kind":"photo (CC0)","alt":"...","credit":"Author","license":"CC0 1.0","source_url":"https://commons.wikimedia.org/wiki/File:...","note":"anything needing a later check"}`
  `crop` = fractions of the source: `[left, top, width]`; height is derived (1200:630). Check the crop visually.
- **Press image, fair-use illustration** (only where legal and clearly editorial about that product/event): save a *small, low-resolution* copy in `src-img/`, then use `"kind":"press image (fair use)"`, `credit` = company/photographer, `source_url` = the page you took it from, and a `note` saying why it's used. Never use stock-agency images (Getty, Shutterstock, AP, Reuters, etc.).
- Always write real `alt` text. `build.py` outputs a 1200×630 JPEG (used for og:image/twitter), plus 1200w and 600w WebP for the page (lazy-loaded, width/height set). `images.md` is regenerated on each build with source and licence per image — put anything needing a licence double-check in `note`.

### 4. Build, commit, deploy, ping
```bash
python3 build.py
git add -A && git commit -m "Add: <title>" && git push
```
Pages redeploys in about a minute. Then ping IndexNow with the sitemap URLs (POST `https://api.indexnow.org/indexnow` with `host`, `key`, `keyLocation=https://humanoidbeat.com/<key>.txt`, `urlList`).

## Changing the domain
Edit `SITE_URL`, run `python3 build.py`, update `docs/CNAME`, push, set the domain in repo Settings → Pages, enforce HTTPS, resubmit sitemap/IndexNow.

## Accessibility / performance notes
Dark theme tuned for WCAG AA contrast, visible focus rings, skip link, `prefers-reduced-motion` disables all animation, no external fonts or libraries, ~3 KB JS, external cached CSS.
