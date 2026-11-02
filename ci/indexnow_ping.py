#!/usr/bin/env python3
"""IndexNow ping: tell IndexNow (Bing, Yandex, Seznam, Naver...) which pages
on humanoidbeat.com changed, right after a publish.

Reads SITE_URL and INDEXNOW_KEY straight out of build.py so there is one
place to change the domain or rotate the key. No third-party dependencies
(stdlib urllib only), so CI doesn't need an extra pip install.

Used by:
  .github/workflows/publish-scheduled.yml  - after the scheduled bot pushes
  .github/workflows/indexnow-on-push.yml   - after any other push to main
                                              that touches docs/

Usage:
  python3 ci/indexnow_ping.py                   # auto-detect changed docs/*.html vs HEAD, POST
  python3 ci/indexnow_ping.py --base HEAD~1      # diff against a different ref
  python3 ci/indexnow_ping.py --changed-file f   # read changed docs-relative paths from a file (one per line)
  python3 ci/indexnow_ping.py --dry-run          # print the payload, skip the network call
  python3 ci/indexnow_ping.py --selftest         # run built-in checks, no network
"""
import json, os, re, subprocess, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://api.indexnow.org/indexnow"


def _config():
    src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
    site = re.search(r'SITE_URL\s*=\s*"([^"]+)"', src).group(1).rstrip("/")
    key = re.search(r'INDEXNOW_KEY\s*=\s*"([^"]+)"', src).group(1)
    return site, key


def doc_path_to_url(site_url, path):
    """'docs/news/x.html' -> '{site}/news/x.html'; 'docs/index.html' -> '{site}/'."""
    rel = path.split("docs/", 1)[-1] if "docs/" in path else path
    if rel in ("index.html", ""):
        return site_url + "/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"{site_url}/{rel}"


def changed_docs_paths(base):
    """docs/**/*.html paths changed since `base` (tracked edits + new, untracked files)."""
    out = set()
    try:
        r = subprocess.run(["git", "diff", "--name-only", base, "--", "docs"],
                            cwd=ROOT, capture_output=True, text=True, check=True)
        out.update(r.stdout.splitlines())
    except subprocess.CalledProcessError:
        pass
    try:
        r = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", "docs"],
                            cwd=ROOT, capture_output=True, text=True, check=True)
        out.update(r.stdout.splitlines())
    except subprocess.CalledProcessError:
        pass
    return sorted(p for p in out if p.endswith(".html"))


def build_url_list(site_url, changed_paths):
    urls = [doc_path_to_url(site_url, p) for p in changed_paths]
    urls += [f"{site_url}/sitemap.xml", f"{site_url}/news-sitemap.xml"]
    seen, ordered = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def ping(site_url, key, url_list, dry_run=False):
    host = site_url.split("://", 1)[-1]
    payload = {"host": host, "key": key, "keyLocation": f"{site_url}/{key}.txt", "urlList": url_list}
    if dry_run:
        return None, payload
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
                                  headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, payload
    except urllib.error.HTTPError as e:
        return e.code, payload
    except urllib.error.URLError as e:
        print(f"IndexNow ping failed (network): {e}", file=sys.stderr)
        return None, payload


def _selftest():
    site = "https://humanoidbeat.com"
    assert doc_path_to_url(site, "docs/index.html") == site + "/"
    assert doc_path_to_url(site, "docs/news/x.html") == site + "/news/x.html"
    assert doc_path_to_url(site, "docs/topics/y.html") == site + "/topics/y.html"

    urls = build_url_list(site, ["docs/index.html", "docs/news/x.html", "docs/index.html"])
    assert urls == [site + "/", site + "/news/x.html", site + "/sitemap.xml", site + "/news-sitemap.xml"], urls

    status, payload = ping(site, "testkey", urls, dry_run=True)
    assert status is None
    assert payload["host"] == "humanoidbeat.com"
    assert payload["key"] == "testkey"
    assert payload["keyLocation"] == site + "/testkey.txt"
    assert payload["urlList"] == urls

    site_url, key = _config()
    assert site_url.startswith("https://") and key, (site_url, key)
    print("selftest ok:", site_url, key)


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0

    dry_run = "--dry-run" in argv
    base = argv[argv.index("--base") + 1] if "--base" in argv else "HEAD"
    changed_file = argv[argv.index("--changed-file") + 1] if "--changed-file" in argv else None

    site_url, key = _config()
    if changed_file:
        with open(changed_file, encoding="utf-8") as f:
            changed = [ln.strip() for ln in f if ln.strip()]
    else:
        changed = changed_docs_paths(base)

    url_list = build_url_list(site_url, changed)
    print(f"IndexNow: {len(url_list)} URL(s) -> {ENDPOINT}")
    for u in url_list:
        print(" ", u)

    status, _ = ping(site_url, key, url_list, dry_run=dry_run)
    print("IndexNow response status:", status if status is not None else "(dry-run / network error)")
    # Best-effort: IndexNow being unreachable shouldn't fail the publish job.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
