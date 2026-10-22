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

### 3. Images (house rule: AI-generated hyper-realistic photos)
Every article gets one AI-generated, hyper-realistic 16:9 photo, supplied as a file via `/workspace` (e.g. `/workspace/humanoid-assets/<name>.jpg`, ideally 1920x1080 or at least 1280x720). Steps:
1. Copy it into `src-img/` (e.g. `cp /workspace/humanoid-assets/x.jpg src-img/<slug>.jpg`).
2. Add to the article in `content/articles.json`:
   `"image":{"src":"src-img/<slug>.jpg","crop":[0,0.05,1.0],"ai":true,"alt":"Describe what is visible","note":"Generic AI-generated scene; not a photo of the actual product/event"}`
   `crop` = `[left, top, width]` as fractions of the source; height is derived (1200:630). Check the crop visually.
3. The build outputs a 1200x630 JPEG (og:image/twitter), plus 600w/1200w WebP (lazy-loaded, width/height set) and shows the caption **"AI-generated image"** under the picture. Captions are automatic for `"ai":true`; never remove them.
4. `images.md` is regenerated on every build with the licence note "generated, owned by Joshua Israel Ventures LLC". Open items go in `TODO_IMAGES` at the top of `build.py` (they print under "TODO" in `images.md`).
- AI photos must depict generic scenes: don't depict real people, real logos or a specific real product/event as if it were a photograph of it. Say so in `note` when the article is about a specific robot.
- **All images must be photoreal** (no cartoons, vector art or illustrations). The old generated-illustration (`art`) option has been removed from `build.py`; if no photo has been supplied yet, publish the article without an image rather than using an illustration. Third-party photos (CC0, press) are no longer the default; if one is ever used, give `kind`, `credit`, `license`, `source_url` and no `ai` flag, and never use stock-agency images.
- Homepage hero: `src-img/humanoid-hero-photo.jpg` (1200/1920 WebP + JPEG, preloaded for LCP) and also the default og:image. To change it, replace that file and rebuild.

### 3b. Inline images (AI-generated, throughout each article)
House rule for every news article: a hero plus an AI-generated inline image roughly every 2-3 paragraphs (short articles: at least one, after paragraph 2).
1. Grok Bot generates the picture and saves it as `/workspace/humanoid-assets/<article-slug>-N.jpg` (N = 1, 2, ...; 16:9, at least 1280 px wide). Never generate or use images of real people, real logos on products, or fabricated events; keep scenes generic and say so in `note`.
2. In the article in `content/articles.json` add (one object per image):
   `"inline_images":[{"file":"<slug>-1.jpg","alt":"Descriptive alt text of what is visible","caption":"Scene: ... (optional)","insert_after_paragraph":2,"brief":"prompt/scene description for the generator","note":"Generic illustration; not a photo of ..."}]`
   - `file`: name inside `/workspace/humanoid-assets/` (or an absolute path).
   - `insert_after_paragraph`: 1-based; `2` puts the figure after the second paragraph of `body`. Several images may use different numbers.
   - `alt`: required, descriptive, plain text. `caption`: optional description; the build always appends **"AI-generated image"**.
   - `brief`: optional, only used for the TODO list in `images.md`.
3. Run the build. It copies the source to `src-img/inline/`, writes `docs/img/<slug>-N-600.webp` and `-1200.webp` (width 1200, height from the source aspect), emits `<figure class="inl">` with srcset, `width`/`height`, `loading="lazy"`, the caption, and adds the image to the article's JSON-LD.
4. `images.md` lists every built inline image with licence "generated, owned by Joshua Israel Ventures LLC". Entries whose file is not there yet are skipped (the site still builds) and listed under "TODO (images)" in `images.md`; the build prints `[inline pending]`.
5. Check the figure visually, then commit including `src-img/inline/`.

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
