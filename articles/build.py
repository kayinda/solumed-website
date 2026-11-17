#!/usr/bin/env python3
"""Build the Articles section of solumedplus.com.

Write each piece as a text file in articles/src/ (see README.md in that folder), then run:

    python3 articles/build.py

It writes articles/<slug>.html for every piece, the list page articles/index.html, the RSS feed
articles/feed.xml, and refreshes the /articles/ lines in sitemap.xml. Then commit and push as usual.
"""
import html, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
SITE = os.path.dirname(HERE)
BASE = "https://solumedplus.com"
CSS_VER = "20261117b"


# ---------- tiny Markdown reader (headings, lists, bold, italic, links) ----------
LINK = re.compile(r"\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")  # URLs may hold (..), e.g. Lancet DOIs
SOURCES = {}  # number -> (url, plain text) for the piece being built


def cite_link(m):
    out = []
    for part in m.group(1).split(","):
        a, _, b = part.partition("-")
        nums = range(int(a), int(b or a) + 1)
        for n in nums:
            url, txt = SOURCES.get(n, (None, ""))
            href = url or f"#src-{n}"
            ext = ' target="_blank" rel="noopener"' if url else ""
            out.append(f'<a href="{html.escape(href)}"{ext} title="{html.escape(txt)}">{n}</a>')
    return '<sup class="cite">[' + ",".join(out) + "]</sup>"


def inline(t, cites=True):
    t = html.escape(t, quote=False)
    t = LINK.sub(lambda m: f'<a href="{m.group(2)}"' +
                 (' target="_blank" rel="noopener"' if m.group(2).startswith("http") else "") +
                 f'>{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    if cites:
        t = re.sub(r"\[(\d+(?:[,-]\d+)*)\](?![(\w])", cite_link, t)
    return t


def read_sources(body):
    """Pull the numbered list under '### Sources' so in-text [n] can link straight to each source."""
    SOURCES.clear()
    m = re.search(r"^###\s+Sources\s*$(.*)", body, re.M | re.S)
    if not m:
        return
    for line in m.group(1).splitlines():
        mm = re.match(r"^\s*(\d+)\.\s+(.*)", line)
        if mm:
            link = LINK.search(mm.group(2))
            plain = LINK.sub(lambda x: x.group(1), mm.group(2))
            SOURCES[int(mm.group(1))] = (link.group(2) if link else None, plain)


def md_to_html(md):
    out, para, lst = [], [], None
    in_sources = False

    def flush():
        nonlocal para, lst
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag, items = lst
            if in_sources and tag == "ol":
                out.append('<ol class="sources">' + "".join(
                    f'<li id="src-{k}">{inline(i, cites=False)}</li>' for k, i in enumerate(items, 1)) + "</ol>")
            else:
                out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        m = re.match(r"^(#{2,4})\s+(.*)", line)
        if m:
            flush()
            n = len(m.group(1))
            in_sources = m.group(2).strip().lower() == "sources"
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            continue
        m = re.match(r"^\s*([-*]|\d+\.)\s+(.*)", line)
        if m:
            if para:
                flush()
            tag = "ol" if m.group(1)[0].isdigit() else "ul"
            if not lst or lst[0] != tag:
                flush(); lst = (tag, [])
            lst[1].append(m.group(2))
            continue
        if lst and raw.startswith("  "):
            lst[1][-1] += " " + line.strip()
            continue
        if lst:
            flush()
        para.append(line.strip())
    flush()
    return "\n".join(out)


def read_piece(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    if not m:
        sys.exit(f"{path}: missing the --- header block")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    for k in ("title", "date", "summary"):
        if not meta.get(k):
            sys.exit(f"{path}: header needs '{k}:'")
    meta.setdefault("type", "Article")
    meta.setdefault("author", "Kayinda Francis")
    meta.setdefault("topic", "")
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["date_obj"] = date.fromisoformat(meta["date"])
    body = m.group(2)
    words = len(re.sub(r"### Sources.*", "", body, flags=re.S).split())
    meta["minutes"] = max(1, round(words / 220))
    read_sources(body)
    meta["body_html"] = md_to_html(body)
    meta["draft"] = meta.get("draft", "").lower() in ("yes", "true")
    return meta


def nice_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


# ---------- page parts ----------
def head(title, desc, canonical, extra=""):
    e = html.escape
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H4STZ0XTSN"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-H4STZ0XTSN');
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Solumed Plus">
<meta property="og:image" content="{BASE}/img/mark-512.png">
<link rel="alternate" type="application/rss+xml" title="Solumed Plus Articles" href="{BASE}/articles/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<meta name="theme-color" content="#0B4F8A">
<link rel="stylesheet" href="../site.css?v={CSS_VER}">
{extra}</head>
<body>

<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="../index.html"><img class="logo" src="../img/mark.svg" alt="" width="40" height="40">
      <span><b>Solumed <span class="plus">Plus</span></b><small>Limited</small></span></a>
    <button class="menu-btn" id="menuBtn" aria-label="Menu">☰</button>
    <nav class="nav-links" id="navLinks">
      <a href="../index.html">Home</a>
      <a href="../software.html">Software</a>
      <a href="../research.html">Research &amp; Innovation</a>
      <a href="index.html" class="active">Articles</a>
      <a class="nav-cta" href="../index.html#contact">Contact</a>
    </nav>
  </div>
</header>
"""


FOOT = """
<footer class="foot">
  <div class="wrap">
    <div>
      <div class="brand" style="margin-bottom:6px"><img class="logo" src="../img/mark-dark.svg" alt="" width="40" height="40"><b>Solumed <span class="plus">Plus</span> Limited</b></div>
      <div class="tag">Solving Health. Scaling Solutions.</div>
      <div class="pillars">Healthcare · Technology · Research</div>
      <p style="font-size:13px;margin-top:12px">Health research &amp; innovation and business software - built in Uganda for East Africa.</p>
    </div>
    <div><h4>Our work</h4>
      <a href="../software.html">Software Solutions</a><a href="../sbm.html">Business Manager</a>
      <a href="../research.html">Research &amp; Innovation</a>
      <a href="index.html">Articles</a></div>
    <div><h4>Contact</h4>
      <a href="mailto:info@solumedplus.com">info@solumedplus.com</a>
      <a href="https://wa.me/256775377245">WhatsApp 0775 377 245</a>
      <a href="../index.html#contact">Send an enquiry</a></div>
  </div>
  <div class="foot-bottom">Kampala, Uganda: +256 775 377 245 &nbsp;·&nbsp; Copyright © Solumed Plus Limited 2026</div>
</footer>

<script>
  var mb=document.getElementById('menuBtn'),nl=document.getElementById('navLinks');
  mb.addEventListener('click',function(){nl.classList.toggle('open');});
  nl.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){nl.classList.remove('open');});});
  var cp=document.getElementById('copyLink');
  if(cp){cp.addEventListener('click',function(){try{navigator.clipboard.writeText(location.href);cp.textContent='Link copied';}catch(e){}});}
  var GC="kaysfrancis";if(GC){var g=document.createElement('script');g.async=true;g.src='//gc.zgo.at/count.js';
    g.setAttribute('data-goatcounter','https://'+GC+'.goatcounter.com/count');document.body.appendChild(g);}
</script>
</body>
</html>
"""

DISCLAIMER = ("This article is general health information, not medical advice. If you or someone in your care "
              "is unwell, see a qualified health worker. Views are the author's own.")


def article_page(a):
    e = html.escape
    url = f"{BASE}/articles/{a['slug']}.html"
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
          f'"headline":{jsq(a["title"])},"description":{jsq(a["summary"])},"datePublished":"{a["date"]}",'
          f'"author":{{"@type":"Person","name":{jsq(a["author"])}}},'
          '"publisher":{"@type":"Organization","name":"Solumed Plus Limited",'
          f'"logo":{{"@type":"ImageObject","url":"{BASE}/img/mark-512.png"}}}},'
          f'"mainEntityOfPage":"{url}"}}</script>\n<meta property="og:type" content="article">\n')
    share = ("https://wa.me/?text=" +
             re.sub(r"[^A-Za-z0-9\-_.~]", lambda m: "%%%02X" % ord(m.group(0)), a["title"] + " " + url))
    topic = f' · {e(a["topic"])}' if a["topic"] else ""
    return head(f"{a['title']} - Solumed Plus", a["summary"], url, ld) + f"""
<div class="hero compact art-hero">
  <div class="wrap">
    <p class="art-kicker">{e(a['type'])}{topic}</p>
    <h1>{e(a['title'])}</h1>
    <p class="art-meta">By {e(a['author'])} · {nice_date(a['date_obj'])} · {a['minutes']} min read</p>
  </div>
</div>

<section>
  <div class="wrap">
    <article class="prose">
      <p class="art-lede">{e(a['summary'])}</p>
{a['body_html']}
      <div class="art-note">{DISCLAIMER}</div>
      <div class="art-share">
        <a class="btn btn-ghost" href="{share}" target="_blank" rel="noopener">Share on WhatsApp</a>
        <button class="btn btn-ghost" id="copyLink" type="button">Copy link</button>
        <a class="btn btn-orange" href="index.html">More articles →</a>
      </div>
    </article>
  </div>
</section>
""" + FOOT


def jsq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def index_page(items):
    e = html.escape
    cards = []
    for a in items:
        topic = f' · {e(a["topic"])}' if a["topic"] else ""
        cards.append(f"""      <a class="card art-card" href="{a['slug']}.html">
        <span class="art-tag">{e(a['type'])}{topic}</span>
        <h3>{e(a['title'])}</h3>
        <p>{e(a['summary'])}</p>
        <span class="art-meta2">{nice_date(a['date_obj'])} · {a['minutes']} min read</span>
      </a>""")
    body = "\n".join(cards) or '      <p style="text-align:center;color:var(--muted)">New articles are on the way.</p>'
    return head("Articles - Solumed Plus", "Plain-language articles and news on health in Uganda from Solumed "
                "Plus Research: antibiotic resistance, medicines, health systems and digital health.",
                f"{BASE}/articles/") + f"""
<div class="hero compact">
  <div class="wrap">
    <h1>Articles</h1>
    <p class="tagline">Health in Uganda, explained plainly</p>
    <p class="sub">Explainers, commentary and news from Solumed Plus Research on antibiotic resistance, medicines, health systems and digital health. Every piece cites its sources.</p>
  </div>
</div>

<section>
  <div class="wrap">
    <div class="art-list">
{body}
    </div>
    <p class="art-rss"><a href="feed.xml">RSS feed</a> · Articles here are general health information, not medical advice. If you are unwell, see a qualified health worker. Views are the authors' own.</p>
  </div>
</section>
""" + FOOT


def feed(items):
    e = html.escape
    rows = []
    for a in items:
        u = f"{BASE}/articles/{a['slug']}.html"
        rows.append(f"<item><title>{e(a['title'])}</title><link>{u}</link><guid>{u}</guid>"
                    f"<pubDate>{a['date_obj'].strftime('%a, %d %b %Y')} 08:00:00 +0300</pubDate>"
                    f"<description>{e(a['summary'])}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>Solumed Plus Articles</title><link>{BASE}/articles/</link>"
            "<description>Health in Uganda, explained plainly.</description><language>en</language>"
            + "".join(rows) + "</channel></rss>\n")


def update_sitemap(items):
    p = os.path.join(SITE, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"  <url><loc>https://solumedplus.com/articles/[^\n]*\n", "", s)
    newest = max([a["date"] for a in items], default=date.today().isoformat())
    lines = [f"  <url><loc>{BASE}/articles/</loc><lastmod>{newest}</lastmod></url>\n"]
    lines += [f"  <url><loc>{BASE}/articles/{a['slug']}.html</loc><lastmod>{a['date']}</lastmod></url>\n"
              for a in items]
    s = s.replace("</urlset>", "".join(lines) + "</urlset>")
    open(p, "w", encoding="utf-8").write(s)


def main():
    items = [read_piece(os.path.join(SRC, f)) for f in sorted(os.listdir(SRC))
             if f.endswith((".md", ".txt")) and not f.startswith(("_", ".")) and f != "README.md"]
    for a in items:
        if "—" in a["body_html"] + a["title"] + a["summary"]:
            print(f"warning: em dash in {a['slug']}")
    live = sorted([a for a in items if not a["draft"]], key=lambda a: a["date"], reverse=True)
    for a in items:
        open(os.path.join(HERE, a["slug"] + ".html"), "w", encoding="utf-8").write(article_page(a))
        print(("draft  " if a["draft"] else "built  ") + f"articles/{a['slug']}.html")
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(index_page(live))
    open(os.path.join(HERE, "feed.xml"), "w", encoding="utf-8").write(feed(live))
    update_sitemap(live)
    print(f"index lists {len(live)} piece(s); feed.xml and sitemap.xml updated")


if __name__ == "__main__":
    main()
