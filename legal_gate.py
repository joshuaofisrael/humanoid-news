#!/usr/bin/env python3
"""Pre-publish legal-hold gate for humanoidbeat.com (Joshua's global rule, 27 Oct 2026).

Full rule: /workspace/content-review/RULE.md. This gate runs inside build.py (the real publishing
step) and in GitHub Actions (.github/workflows/legal-gate.yml).

What it does for every article in content/articles.json:
  * code checks: >=1 http(s) source URL (rule 4); every hero/inline image has a provenance record in
    content/image-provenance.json whose sha256 matches the file (own AI images need the generation
    prompt; anything else needs documented permission, otherwise rule 3); AI caption present;
    pattern flags for rules 1, 2, 5, 6, 7 and 8.
  * any flag => status HOLD_REVIEW: the article is NOT rendered, a draft is saved and one JSON line is
    appended to /workspace/content-review/queue.jsonl (deduped by slug+sha256+rule).
  * a held article passes only when /workspace/content-review/approvals.jsonl holds Joshua's approval
    for this site + slug with the exact sha256 (mirrored to content/legal-approved.json for CI).
    MODERATE-only holds (rules 3,4,5,7) may also pass via a moderate-clearances.jsonl record with the
    exact sha256 and chatgpt_verdict SAFE (Joshua's 18:25 amendment). HIGH (1,2,6,8) never do.
  * articles that were already live when the gate was installed and are unchanged since (exact
    sha256 in content/legal-baseline.json) keep rendering even if flagged (no automatic unpublishing);
    their flags are logged as HOLD_REVIEW notes. Any edit drops the grandfathering and re-checks.
This module NEVER writes approvals or clearances.
"""
import json, os, re, sys, hashlib, datetime

SITE = "humanoidbeat.com"; BOT = "Humanoid News"
REVIEW_DIR = os.environ.get("CONTENT_REVIEW_DIR", "/workspace/content-review")
HERE = os.path.dirname(os.path.abspath(__file__))
PROV = os.path.join(HERE, "content", "image-provenance.json")
BASELINE = os.path.join(HERE, "content", "legal-baseline.json")
MIRROR = os.path.join(HERE, "content", "legal-approved.json")
ASSETS_DIR = "/workspace/humanoid-assets"
HIGH = {1, 2, 6, 8}

# ---- pattern rules (deliberately broad: a false positive costs a review, a miss can cost a lawsuit)
P = {
 1: r"\b(fraud\w*|embezzl\w*|brib(e|es|ed|ery|ing)|corrupt\w*|launder\w*|scam\w*|ponzi|criminal\w*|crimes?|arrest\w*|indict\w*|charged with|convict\w*|alleg\w*|accus\w*|misconduct|abus(e|ed|es|ive|ing)|harass\w*|lied (to|about)|lying (to|about)|cover-?up|decei\w*|deceptive|misled|negligen\w*|theft|stole|stolen|steal\w*|espionage|wrongdoing|unlawful\w*|illegal\w*|lawsuit\w*|sued|suing|infring\w*|counterfeit\w*|price-?fixing|cartel)\b",
 2: r"([\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d ()-]{8,}\d|\bhome address|\bdate of birth|\bsocial security|\bpassport number|\bbank account|\bmedical (record|history|condition)s?|\bdiagnos(ed|is) with|\bsexual orientation|\bHIV\b|\bvictims?\b|\bminors\b|\b(named|identified) (child|children|teenager|pupil|patient)s?\b|\bleaked (document|email|memo|message)s?|\bprivate (message|email|chat)s?)",
 5: r"\b(you should (buy|sell|invest|short|take)|we recommend (buying|selling|investing)|(buy|sell) (the|this|its) (stock|shares)|guaranteed (returns?|profits?|income|gains?)|risk-free (returns?|profits?)|will (double|triple) your|price target|dosage|how to (build|make) (a |an )?(bomb|weapon|explosive|gun))\b",
 6: r"\b(polling (place|station|location)s?|voter registration|register to vote|registration deadline|election day|absentee|mail-in ballots?|early voting|ballots?|certified (result|winner)s?|vote counts?|voting (hours|location|rules|eligibility)|primary election|general election|midterms?)\b",
 7: r"\b(confirm(s|ed)?|proves?|proven|officially|guarantee[sd]?|first[- ]ever|world'?s first|breakthrough|revolution\w*|shock\w*|destroy\w*|slams?|endorse[sd]?|partner(ed|ship)? with HumanoidBeat|exclusive)\b",
 8: r"\b(cease and desist|legal notice|takedown (notice|request)|DMCA|under embargo|embargo(ed)? until|embargo|court order|injunction|gag order|reporting restrictions?|correction request|right of reply|defamation|libel\w*|copyright (claim|complaint|notice))\b",
}
RULE_NAME = {1: "damaging allegation", 2: "sensitive personal info", 3: "unclear content rights", 4: "unsupported claim / no source",
             5: "high-impact guidance", 6: "election information", 7: "misleading presentation", 8: "legal complaint / restriction"}
SUGGEST = {1: "Joshua to review the exact wording; do not soften to dodge review. Approve this exact version or remove the allegation.",
           2: "Remove the personal/sensitive detail or get Joshua's approval of this exact version.",
           3: "Record provenance (own AI image: generation prompt + sha256) or documented permission, or drop the image and re-run the build.",
           4: "Add a source URL that was actually accessed and supports every material claim.",
           5: "Reframe as attributed reporting, not advice; check no returns are promised.",
           6: "Confirm every election logistics detail with the relevant election authority, then Joshua approves.",
           7: "Make the headline match the evidence (attribute: 'X says'); label synthetic media clearly.",
           8: "Send to the Personal assistant with priority; never republish automatically."}

def sha(article):
    a = {k: v for k, v in article.items() if not k.startswith("_")}
    return hashlib.sha256(json.dumps(a, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

def file_sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None

def _jl(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try: out.append(json.loads(line))
                except Exception: pass
    return out

def _load(path, default):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default

def strip(s): return re.sub(r"<[^>]+>", " ", s or "")

def inline_path(spec):
    f = spec["file"]; keep = os.path.join(HERE, "src-img", "inline", os.path.basename(f))
    p = f if os.path.isabs(f) else os.path.join(ASSETS_DIR, f)
    return p if os.path.exists(p) else (keep if os.path.exists(keep) else None)  # same order as build.make_inline

def images(a):
    out = []
    if a.get("image"): out.append(("hero", os.path.join(HERE, a["image"]["src"]), a["image"]))
    for n, sp in enumerate(a.get("inline_images", []), 1):
        p = inline_path(sp)
        if p: out.append((f"inline-{n}", p, sp))  # not-yet-supplied inline images are not rendered by build.py
    return out

def check(a, prov=None):
    """Return list of (rule, flagged_text) for one article (or synthetic item)."""
    prov = _load(PROV, {}) if prov is None else prov
    flags = []
    srcs = [s.get("url", "") for s in a.get("sources", [])]
    if not any(re.match(r"https?://[^\s/]+\.[^\s/]+", u) for u in srcs): flags.append((4, "no source URL"))
    if not a.get("title") or not a.get("body"): flags.append((4, "missing title/body"))
    for kind, path, spec in images(a):
        rel = os.path.relpath(path, HERE) if path.startswith(HERE) else os.path.basename(path)
        if kind.startswith("inline"): rel = "src-img/inline/" + os.path.basename(path)
        rec = prov.get(rel)
        h = file_sha(path)
        if not rec: flags.append((3, f"{kind} image {rel}: no provenance/licence record")); continue
        if rec.get("sha256") != h: flags.append((3, f"{kind} image {rel}: file differs from provenance record (sha256)")); continue
        if rec.get("origin") == "ai-generated":
            if not (rec.get("prompt") or rec.get("legacy")): flags.append((3, f"{kind} image {rel}: AI image without recorded prompt"))
            if kind == "hero" and not spec.get("ai"): flags.append((7, f"hero image {rel}: AI image not marked ai:true (caption 'AI-generated image' would be missing)"))
        elif rec.get("origin") == "licensed":
            if not (rec.get("permission") and rec.get("permission_doc")): flags.append((3, f"{kind} image {rel}: third-party image without documented permission"))
        else: flags.append((3, f"{kind} image {rel}: unknown origin '{rec.get('origin')}'"))
        if not spec.get("alt"): flags.append((7, f"{kind} image {rel}: no alt text"))
    fields = [("title", a.get("title", "")), ("summary", a.get("summary", "")), ("seo_title", a.get("seo_title", ""))] + \
             [("body", strip(p)) for p in a.get("body", [])] + [("analysis", strip(p)) for p in a.get("analysis", [])] + \
             [("why", strip(p)) for p in a.get("why", [])] + [("image", (sp.get("alt", "") + " " + sp.get("caption", ""))) for _, _, sp in images(a)]
    for rule in (1, 2, 5, 6, 8):
        for name, txt in fields:
            for m in re.finditer(P[rule], txt, re.I):
                s = max(0, m.start() - 70); flags.append((rule, f"{name}: …{txt[s:m.end() + 70].strip()}…")); break
    for name in ("title", "seo_title"):
        txt = a.get(name, "")
        m = re.search(P[7], txt, re.I)
        if m: flags.append((7, f"{name}: {txt}"))
    seen, out = set(), []
    for r, t in flags:
        if (r, t) not in seen: seen.add((r, t)); out.append((r, t))
    return out

def approved(slug, h, rules):
    for r in _jl(os.path.join(REVIEW_DIR, "approvals.jsonl")) + _load(MIRROR, []):
        if r.get("site") == SITE and r.get("sha256") == h and r.get("slug", slug) == slug and str(r.get("approved_by", "Joshua")).lower().startswith("joshua"):
            return "approval"
    if not (set(rules) & HIGH):
        for r in _jl(os.path.join(REVIEW_DIR, "moderate-clearances.jsonl")):
            if r.get("site") == SITE and r.get("sha256") == h and str(r.get("chatgpt_verdict", "")).upper().startswith("SAFE"):
                return "moderate-clearance"
    return None

def log_hold(a, h, flags, note="", draft=True, queue=None):
    queue = queue or os.path.join(REVIEW_DIR, "queue.jsonl")
    if not os.path.isdir(os.path.dirname(queue)): return None
    rules = sorted({r for r, _ in flags})
    dp = ""
    if draft:
        dd = os.path.join(REVIEW_DIR, "drafts", "humanoidbeat"); os.makedirs(dd, exist_ok=True)
        dp = os.path.join(dd, f"{a.get('slug','item')}.{h[:12]}.HOLD_REVIEW.json")
        if not os.path.exists(dp): json.dump({"status": "HOLD_REVIEW", "sha256": h, "flags": flags, "article": {k: v for k, v in a.items() if not k.startswith("_")}}, open(dp, "w"), indent=1, ensure_ascii=False)
    key = (a.get("slug"), h, tuple(rules))
    for r in _jl(queue):
        if r.get("site") == SITE and (r.get("slug"), r.get("sha256"), tuple(r.get("rule") if isinstance(r.get("rule"), list) else [r.get("rule")])) == key:
            return dp
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "site": SITE, "bot": BOT, "title": a.get("title", ""),
           "slug": a.get("slug"), "sha256": h, "flagged": " | ".join(t for _, t in flags)[:1500], "rule": rules,
           "severity": "HIGH" if set(rules) & HIGH else "MODERATE", "sources": [s.get("url") for s in a.get("sources", [])],
           "suggestion": " ".join(SUGGEST[r] for r in rules) + (" " + note if note else ""), "draft_path": dp, "status": "HOLD_REVIEW"}
    with open(queue, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return dp

def apply(articles, log=True):
    """Called by build.py. Returns (publishable_articles, report). Held, unapproved, non-grandfathered items are removed."""
    prov = _load(PROV, None)
    if not os.path.exists(BASELINE): raise SystemExit("LEGAL GATE: content/legal-baseline.json missing; refusing to build.")
    if prov is None: raise SystemExit("LEGAL GATE: content/image-provenance.json missing; refusing to build.")
    base = {b["slug"]: b["sha256"] for b in _load(BASELINE, [])}
    keep, report = [], {"held": [], "grandfathered": [], "approved": [], "passed": 0}
    for a in articles:
        h = sha(a); fl = check(a, prov); rules = sorted({r for r, _ in fl})
        if not fl: keep.append(a); report["passed"] += 1; continue
        how = approved(a["slug"], h, rules)
        if how: keep.append(a); report["approved"].append((a["slug"], how)); continue
        if base.get(a["slug"]) == h:
            keep.append(a); report["grandfathered"].append((a["slug"], rules))
            if log: log_hold(a, h, fl, note="Already live before the gate was installed; NOT unpublished automatically. Joshua decides whether to keep, edit or remove.", draft=False)
            continue
        report["held"].append((a["slug"], rules, fl))
        if log: log_hold(a, h, fl)
    for slug, rules, fl in report["held"]:
        print(f"  [HOLD_REVIEW] {slug}: rules {rules} -> not rendered; logged to queue.jsonl")
    for slug, rules in report["grandfathered"]:
        print(f"  [HOLD note, live pre-gate] {slug}: rules {rules} (still rendered, unchanged since baseline)")
    print(f"LEGAL GATE: {report['passed']} passed, {len(report['approved'])} approved, {len(report['grandfathered'])} pre-gate notes, {len(report['held'])} held")
    return keep, report

def mirror_approvals():
    """Copy Joshua's approvals for this site into the repo so CI can see them (never creates approvals)."""
    recs = [r for r in _jl(os.path.join(REVIEW_DIR, "approvals.jsonl")) if r.get("site") == SITE]
    if recs or os.path.exists(os.path.join(REVIEW_DIR, "approvals.jsonl")):
        json.dump(recs, open(MIRROR, "w"), indent=1, ensure_ascii=False)

def ci(docs="docs"):
    """CI: fail if any held, unapproved, non-grandfathered article appears in the published output."""
    arts = _load(os.path.join(HERE, "content", "articles.json"), [])
    _, rep = apply(arts, log=False)
    bad = []
    blobs = "".join(open(os.path.join(HERE, docs, f), encoding="utf-8").read() for f in ("sitemap.xml", "feed.xml", "index.html") if os.path.exists(os.path.join(HERE, docs, f)))
    base = {b["slug"] for b in _load(BASELINE, [])}
    for slug, rules, _ in rep["held"]:
        # an edited pre-gate article keeps its old live file (no auto-unpublish) but must not be re-listed
        if (slug not in base and os.path.exists(os.path.join(HERE, docs, "news", slug + ".html"))) or f"news/{slug}.html" in blobs:
            bad.append((slug, rules))
    if bad:
        print("LEGAL GATE CI FAIL: held content is published:", bad); sys.exit(1)
    print("LEGAL GATE CI OK"); sys.exit(0)

def record_image(path, prompt, generator="Grok Bot GenerateImage"):
    """Helper for the daily routine: record an own AI-generated image with its prompt."""
    prov = _load(PROV, {}); rel = os.path.relpath(os.path.abspath(path), HERE)
    prov[rel] = {"origin": "ai-generated", "generator": generator, "prompt": prompt, "sha256": file_sha(path),
                 "recorded": datetime.date.today().isoformat()}
    json.dump(dict(sorted(prov.items())), open(PROV, "w"), indent=1, ensure_ascii=False); print("recorded", rel)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "ci": ci()
    elif cmd == "record-image": record_image(sys.argv[2], sys.argv[3])
    elif cmd == "scan":
        arts = _load(os.path.join(HERE, "content", "articles.json"), [])
        for a in arts:
            fl = check(a)
            if fl: print(a["slug"], sorted({r for r, _ in fl})); [print("    ", r, t[:220]) for r, t in fl]
