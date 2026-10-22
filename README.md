# Humanoid News
Static humanoid-robotics news site. Owned and operated by Joshua Israel Ventures LLC.
Source of truth: `build.py` → generates `docs/` (served by GitHub Pages).

## Switching to a custom domain
1. In `build.py`, set `SITE_URL = "https://yourdomain.com"` (no trailing slash). Optionally set `EMAIL`.
2. `python3 build.py`
3. `echo yourdomain.com > docs/CNAME`
4. Commit & push; set the custom domain in repo Settings → Pages and enable HTTPS; add DNS records.
5. Submit `https://yourdomain.com/sitemap.xml` to Google Search Console / Bing, and ping IndexNow with the key file in `docs/`.
