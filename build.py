#!/usr/bin/env python3
"""Static site generator for Humanoid News.
DOMAIN CHANGE: edit SITE_URL below, run `python3 build.py`, add CNAME file, commit."""
import json, os, html, datetime
SITE_URL = "https://joshuaofisrael.github.io/humanoid-news"  # <-- ONLY place to change
NAME="Humanoid News"; LLC="Joshua Israel Ventures LLC"; EMAIL="hello@example.com"
INDEXNOW_KEY="7f3c2a9e4b1d4e8a9c6f0b2d5e7a1c34"
DESC="Independent, answer-first news on humanoid robots: Tesla Optimus, Figure, Agility, Boston Dynamics, Unitree, 1X and more."
OUT="docs"
A=[
dict(slug="tesla-optimus-deliveries-late-2027",date="2026-10-22",cat="Tesla",
title="Tesla pushes external Optimus deliveries to late 2027",
summary="Tesla now targets the end of 2027 for delivering Optimus humanoids to outside customers, citing unsolved problems with the hands, durability and AI.",
body=["<strong>Short answer:</strong> On Tesla's Q3 2026 earnings call, Elon Musk said external Optimus deliveries should start around the end of 2027, after the company solves remaining issues with the robot's hands, reliability and AI.",
"Musk said early Optimus production has begun on a high-volume line in Fremont, in space formerly used for Model S and Model X. Most of a line designed for about one million robots a year is installed, but he said reaching that rate could take at least a year because parts of the design are still changing.",
"A Tesla engineer identified the hand as one of the hardest hardware areas, alongside custom gears with reliability concerns. On software, Tesla plans to build 10,000 to 20,000 robots to practise tasks in what it calls an \"Optimus Academy\", and intends to put its AI5 chip in Optimus around April 2027, according to Electrek's account of the call.",
"First external customers are expected to be industrial jobs that are dangerous, repetitive or need round-the-clock operation."],
sources=[("Electrek: Tesla pushes Optimus deliveries to late 2027","https://electrek.co/2026/10/22/tesla-optimus-delivery-late-2027-hands-ai-problems/")]),
dict(slug="fotex-unitree-hive-grocery-restocking-pilot",date="2026-10-22",cat="Unitree",
title="Danish grocer Føtex pilots Unitree humanoids for overnight restocking",
summary="Salling Group's Føtex chain is trialling humanoid robots built on Unitree hardware and HIVE Robots software to restock shelves after closing.",
body=["<strong>Short answer:</strong> Føtex, part of Denmark's Salling Group, has begun a multi-year pilot with Danish start-up HIVE Robots in which humanoid robots restock grocery shelves after hours at a store in Lyngby, north of Copenhagen.",
"Unitree manufactures the robot hardware while HIVE Robots builds the control software and manages machine learning. Trials run after closing time to provide a controlled environment for testing and data collection.",
"In training zones, human \"robot pilots\" use VR headsets and handheld controllers to guide the robots through tasks such as picking up bags of pasta and placing them on shelves. The current prototypes move more slowly than human staff.",
"Føtex says a humanoid form factor lets the robots work in aisles designed for people without costly store redesigns."],
sources=[("ESM Magazine: Føtex pilots humanoid robots","https://www.esmmagazine.com/technology/salling-groups-fotex-pilots-humanoid-robots-via-multi-year-hive-partnership-324091")]),
dict(slug="korea-safety-rules-robros-humanoids-factories",date="2026-10-14",cat="Policy",
title="South Korea eases safety rules to put 20 humanoids on factory floors",
summary="Korean regulators relaxed rules written for stationary industrial robots, clearing the way for 20 Robros humanoids to work in factories.",
body=["<strong>Short answer:</strong> South Korea has eased safety regulations originally written for fixed industrial robots, allowing mobile humanoid robots to work on factory floors. Twenty AI-powered bipedal humanoids from Korean developer Robros are set to be deployed, including at Nepes.",
"Existing rules were designed for stationary robot arms operating behind barriers, which did not fit robots that walk among workers. The change is one of the first regulatory moves anywhere aimed specifically at enabling humanoids in production environments.",
"The deployments span manufacturing settings across several industries, according to the Seoul Economic Daily."],
sources=[("Seoul Economic Daily: Korea clears safety rules for humanoid robots","https://en.sedaily.com/finance/2026/10/14/korea-clears-safety-rules-to-put-20-humanoid-robots-on")]),
dict(slug="nvidia-isaac-agile-one-sn-reference-humanoid",date="2026-10-20",cat="NVIDIA",
title="NVIDIA expands Isaac platform with Agile ONE SN reference humanoid",
summary="NVIDIA announced new Isaac frameworks, simulation pipelines and data, plus a humanoid reference platform from Agile Robots built on Isaac GR00T.",
body=["<strong>Short answer:</strong> NVIDIA has expanded its Isaac robotics platform with new frameworks, simulation pipelines and training data, and Agile Robots announced Agile ONE SN, a humanoid reference platform built on NVIDIA Isaac GR00T.",
"According to NVIDIA, Agile ONE SN runs on NVIDIA Jetson Thor with planned integration of the NVIDIA Halos safety stack, aiming to give developers and researchers a complete platform for humanoid research.",
"Reference designs like this lower the barrier for labs and start-ups that want to work on humanoid software without building hardware from scratch."],
sources=[("NVIDIA Newsroom: NVIDIA advances Isaac platform","https://nvidianews.nvidia.com/news/nvidia-advances-isaac-platform-for-general-purpose-robotics-with-new-reference-humanoid-frameworks-simulation-pipelines-and-data")]),
dict(slug="minerva-humanoids-10m-pre-seed-general-catalyst",date="2026-10-06",cat="Funding",
title="Minerva Humanoids raises $10M to build robots for dangerous jobs",
summary="San Francisco start-up Minerva Humanoids emerged from stealth with about $10 million led by General Catalyst for its semi-autonomous humanoid, Roger.",
body=["<strong>Short answer:</strong> Minerva Humanoids has raised approximately $10 million in pre-seed funding led by General Catalyst, with Long Journey Ventures and Credo Ventures co-leading, to build humanoid robots for hazardous work in oil and gas and public safety.",
"Its robot, Roger, is semi-autonomous: trained specialists apply their expertise remotely while staying physically away from danger, for example when responding to a suspected explosive or doing hazardous work at an energy site.",
"The company was founded by CEO Sandor Felber and CTO Maurice Rahme and says it is launching its first paid pilots this autumn. Other participants include Hugging Face and Codecademy, among others."],
sources=[("Minerva Humanoids press release","https://www.minervahumanoids.com/press/minerva-humanoids-raises-10m-pre-seed-led-by-general-catalyst")]),
]
A.sort(key=lambda a:a["date"],reverse=True)
PUB={"@type":"Organization","name":LLC,"url":SITE_URL+"/","logo":{"@type":"ImageObject","url":SITE_URL+"/favicon.svg"}}
CSS="""*{box-sizing:border-box}body{margin:0;font:17px/1.65 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1d24;background:#f7f8fa}a{color:#0b57d0}a:focus,button:focus{outline:3px solid #f59e0b;outline-offset:2px}.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px}header{background:#0f172a;color:#fff}header .w{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}header a{color:#fff;text-decoration:none}.logo{font-weight:800;font-size:1.3rem}.logo span{color:#38bdf8}nav a{margin-left:16px}.w{max-width:860px;margin:0 auto;padding:16px 20px}.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:18px 22px;margin:16px 0}.card h2{margin:.2em 0;font-size:1.25rem}.meta{color:#475569;font-size:.9rem}.tag{background:#e0f2fe;color:#075985;border-radius:4px;padding:1px 8px;font-size:.8rem;font-weight:600}footer{background:#0f172a;color:#cbd5e1;font-size:.9rem;margin-top:40px}footer a{color:#7dd3fc}h1{line-height:1.25}"""
def esc(s):return html.escape(s,quote=True)
def page(path,title,desc,content,depth,ld=None,typ="website"):
    r="../"*depth; url=SITE_URL+"/"+path.replace("index.html","")
    lds=[{"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE_URL+"/","publisher":PUB}]+([ld] if ld else [])
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta property="og:type" content="{typ}"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}/og.svg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="{NAME}" href="{r}feed.xml">
<style>{CSS}</style>""" + "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds) + f"""</head><body>
<a class="skip" href="#main">Skip to content</a><header><div class="w"><a class="logo" href="{r}index.html">Humanoid<span>News</span></a><nav aria-label="Main"><a href="{r}index.html">News</a><a href="{r}about.html">About</a><a href="{r}about.html#contact">Contact</a><a href="{r}feed.xml">RSS</a></nav></div></header>
<main id="main" class="w">{content}</main>
<footer><div class="w"><p><a href="{r}about.html">About</a> · <a href="{r}terms.html">Terms</a> · <a href="{r}privacy.html">Privacy</a> · <a href="{r}disclaimer.html">Disclaimer</a> · <a href="{r}feed.xml">RSS</a></p>
<p>© 2026 Joshua Israel Ventures LLC. All rights reserved. Humanoid News is owned and operated by Joshua Israel Ventures LLC.</p></div></footer></body></html>"""
    p=os.path.join(OUT,path);os.makedirs(os.path.dirname(p) or OUT,exist_ok=True);open(p,"w").write(h)
def fd(d):return datetime.date.fromisoformat(d).strftime("%-d %B %Y")
os.makedirs(OUT+"/news",exist_ok=True)
cards="".join(f'<article class="card"><span class="tag">{a["cat"]}</span><h2><a href="news/{a["slug"]}.html">{esc(a["title"])}</a></h2><p class="meta"><time datetime="{a["date"]}">{fd(a["date"])}</time></p><p>{esc(a["summary"])}</p></article>' for a in A)
page("index.html",f"{NAME}: Humanoid Robot News & Analysis",DESC,f"<h1>Latest humanoid robot news</h1><p>{DESC}</p>{cards}",0)
for a in A:
    u=f"{SITE_URL}/news/{a['slug']}.html"
    ld={"@context":"https://schema.org","@type":"NewsArticle","headline":a["title"],"description":a["summary"],"datePublished":a["date"],"dateModified":a["date"],"mainEntityOfPage":u,"image":[SITE_URL+"/og.svg"],"author":{"@type":"Organization","name":NAME+" Staff"},"publisher":PUB,"isBasedOn":[s[1] for s in a["sources"]]}
    src="".join(f'<li><a href="{s[1]}" rel="noopener">{esc(s[0])}</a></li>' for s in a["sources"])
    body="".join(f"<p>{p}</p>" for p in a["body"])
    page(f"news/{a['slug']}.html",f"{a['title']} | {NAME}",a["summary"],f'<article class="card"><span class="tag">{a["cat"]}</span><h1>{esc(a["title"])}</h1><p class="meta">By {NAME} Staff · <time datetime="{a["date"]}">{fd(a["date"])}</time></p>{body}<h2>Sources</h2><ul>{src}</ul></article><p><a href="../index.html">← All news</a></p>',1,ld,"article")
L=f"<strong>{LLC}</strong>"
legal={
"about.html":("About",f"<h1>About {NAME}</h1><p>{NAME} is an independent publication covering humanoid robots: the companies, the technology, the deployments and the policy. Every story is written originally, leads with the answer, and links to its primary sources. We do not invent facts or quotes.</p><p>{NAME} is owned and operated by {L}, a Florida limited liability company.</p><h2 id=\"contact\">Contact</h2><p>Tips, corrections and enquiries: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. We correct errors promptly and transparently.</p>"),
"terms.html":("Terms of Use",f"<h1>Terms of Use</h1><p>These Terms govern your use of {NAME}, owned and operated by {L} (\"we\"). By using the site you agree to them.</p><h2>Content</h2><p>All original content is © 2026 {LLC}. You may share links and brief quotations with attribution. Third-party trademarks belong to their owners and are used for identification only.</p><h2>No warranty</h2><p>The site is provided \"as is\" without warranties of any kind. To the fullest extent permitted by law, {LLC} is not liable for any damages arising from your use of the site.</p><h2>Governing law</h2><p>These Terms are governed by the laws of the State of Florida, USA, and any dispute shall be resolved in the state or federal courts located in Florida.</p><h2>Changes</h2><p>We may update these Terms; continued use means acceptance.</p>"),
"privacy.html":("Privacy Policy",f"<h1>Privacy Policy</h1><p>This policy explains how {L}, operator of {NAME}, handles information.</p><h2>What we collect</h2><p>The site sets no cookies and runs no advertising trackers. Our hosting provider may log standard technical data (such as IP address and browser type) for security and operations. If you email us, we keep your message to respond.</p><h2>Sharing</h2><p>We do not sell personal information.</p><h2>Your rights</h2><p>You may request access to or deletion of information you sent us by emailing <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p><h2>Governing law</h2><p>This policy is governed by the laws of the State of Florida, USA.</p>"),
"disclaimer.html":("Disclaimer",f"<h1>Disclaimer</h1><p>Content on {NAME} is for general information only and is not investment, legal or professional advice. We work to verify facts against cited sources but cannot guarantee completeness or accuracy. {NAME} is not affiliated with any company it covers unless stated. {NAME} is owned and operated by {L}, and this disclaimer is governed by the laws of the State of Florida, USA.</p>"),
}
for f,(t,c) in legal.items(): page(f,f"{t} | {NAME}",f"{t} for {NAME}, operated by {LLC}.",c,0)
page("404.html",f"Page not found | {NAME}","Page not found.",'<h1>Page not found</h1><p>That page does not exist. <a href="index.html">Go to the latest news</a>.</p>',0)
# 404 is served at arbitrary depth: make links absolute to site root for it
s=open(OUT+"/404.html").read().replace('href="index.html"',f'href="{SITE_URL}/index.html"').replace('href="about.html',f'href="{SITE_URL}/about.html').replace('href="terms.html',f'href="{SITE_URL}/terms.html').replace('href="privacy.html',f'href="{SITE_URL}/privacy.html').replace('href="disclaimer.html',f'href="{SITE_URL}/disclaimer.html').replace('href="feed.xml',f'href="{SITE_URL}/feed.xml').replace('href="favicon.svg',f'href="{SITE_URL}/favicon.svg').replace('<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">','<meta name="robots" content="noindex">')
open(OUT+"/404.html","w").write(s)
urls=[("",A[0]["date"])]+[(f"news/{a['slug']}.html",a["date"]) for a in A]+[(f,"2026-10-22") for f in legal]
open(OUT+"/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{d}</lastmod></url>" for u,d in urls)+"</urlset>\n")
bots=["Googlebot","Bingbot","GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-Web","anthropic-ai","PerplexityBot","CCBot","Google-Extended","Applebot","Applebot-Extended","Bytespider","Amazonbot","Meta-ExternalAgent"]
open(OUT+"/robots.txt","w").write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)+f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
open(OUT+f"/{INDEXNOW_KEY}.txt","w").write(INDEXNOW_KEY)
open(OUT+"/llms.txt","w").write(f"# {NAME}\n\n> {DESC} Owned and operated by {LLC}.\n\n## Articles\n"+"".join(f"- [{a['title']}]({SITE_URL}/news/{a['slug']}.html): {a['summary']}\n" for a in A)+f"\n## About\n- [About]({SITE_URL}/about.html)\n- [RSS]({SITE_URL}/feed.xml)\n")
def rfc(d):return datetime.datetime.fromisoformat(d+"T12:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
open(OUT+"/feed.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{NAME}</title><link>{SITE_URL}/</link><description>{esc(DESC)}</description><language>en</language><atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'+"".join(f"<item><title>{esc(a['title'])}</title><link>{SITE_URL}/news/{a['slug']}.html</link><guid>{SITE_URL}/news/{a['slug']}.html</guid><pubDate>{rfc(a['date'])}</pubDate><description>{esc(a['summary'])}</description></item>" for a in A)+"</channel></rss>\n")
open(OUT+"/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0f172a"/><rect x="18" y="14" width="28" height="22" rx="6" fill="#38bdf8"/><circle cx="27" cy="25" r="3.5" fill="#0f172a"/><circle cx="37" cy="25" r="3.5" fill="#0f172a"/><rect x="22" y="40" width="20" height="12" rx="3" fill="#38bdf8"/></svg>')
open(OUT+"/og.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#0f172a"/><text x="80" y="330" font-family="sans-serif" font-size="110" font-weight="800" fill="#fff">Humanoid<tspan fill="#38bdf8">News</tspan></text><text x="80" y="420" font-family="sans-serif" font-size="40" fill="#cbd5e1">Independent humanoid robot news</text></svg>')
open(OUT+"/.nojekyll","w").write("")
print("built",len(A),"articles")
