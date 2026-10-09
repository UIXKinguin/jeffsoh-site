"""Build the static site.

Each page lives in src/ as an HTML fragment whose first line is a JSON comment:
    <!-- {"title": "...", "description": "...", "path": "/my-work/terra/", "nav": "work"} -->
The script wraps it in the shared header and footer, fills in image width/height,
makes root-relative links relative (so the site works on any host or sub-path),
and writes <path>/index.html. Run:  python build.py
"""
import html
import json
import os
import posixpath
import re
from datetime import date

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
SITE_URL = "https://www.jeffsoh.com"
EMAIL = "jeffrey.oh.hci@gmail.com"

NAV = [("work", "Work", "/my-work/"), ("projects", "Projects", "/side-projects/"),
       ("about", "About", "/about-me/"), ("contact", "Contact", "/contact/")]

# Old Squarespace URLs that should keep working.
REDIRECTS = {
    "/home/": "/",
    "/general-2/": "/side-projects/",
    "/ev-battery-failure-prediction-agent/": "/side-projects/ev-battery-failure-prediction-agent/",
    "/automated-trading-bot/": "/side-projects/automated-trading-bot/",
    "/my-work/ev-battery-failure-prediction-agent/": "/side-projects/ev-battery-failure-prediction-agent/",
    "/my-work/automated-trading-bot/": "/side-projects/automated-trading-bot/",
}


def header(nav_key):
    items = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == nav_key else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="wordmark" href="/">Jeffrey Oh</a>
    <nav class="site-nav" aria-label="Main">
      <ul>{''.join(items)}</ul>
    </nav>
  </div>
</header>"""


def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <p>&copy; {date.today().year} Jeffrey Oh. Built with HTML and CSS.</p>
    <ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><a href="https://www.linkedin.com/in/jsohci/">LinkedIn</a></li>
      <li><a href="/assets/files/jeffrey-oh-resume.pdf">Resume (PDF)</a></li>
      <li><a href="/why-me/">Why me</a></li>
    </ul>
  </div>
</footer>"""


def page(meta, body):
    title = meta["title"]
    full_title = "Jeffrey Oh" if title == "Jeffrey Oh" else f"{title} | Jeffrey Oh"
    desc = html.escape(meta.get("description", ""), quote=True)
    canonical = SITE_URL + meta["path"]
    og_image = meta.get("image", "/assets/img/og-default.png")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(full_title, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}{og_image}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#111113" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
{header(meta.get("nav"))}
<main id="main" tabindex="-1">
{body.strip()}
</main>
{footer()}
</body>
</html>
"""


def size_images(doc):
    """Add width/height and lazy loading to every local <img>."""
    def fix(m):
        tag = m.group(0)
        src = re.search(r'src="(/assets/[^"]+)"', tag)
        if src and "width=" not in tag:
            path = os.path.join(ROOT, src.group(1).lstrip("/"))
            with Image.open(path) as im:
                w, h = im.size
            tag = tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)
        if "data-eager" in tag:
            tag = tag.replace(" data-eager", ' fetchpriority="high"')
        elif "loading=" not in tag:
            tag = tag.replace("<img ", '<img loading="lazy" decoding="async" ', 1)
        if 'alt="' not in tag:
            raise ValueError(f"image without alt: {tag}")
        return tag
    return re.sub(r"<img\b[^>]*>", fix, doc)


def smart_quotes(body):
    """Curly quotes and apostrophes in text only, never inside tags or attributes."""
    parts = re.split(r"(<[^>]+>)", body)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        part = re.sub(r"(\w)'(\w)", r"\1’\2", part)
        part = re.sub(r"(^|[\s(\[])'", r"\1‘", part)
        part = part.replace("'", "’")
        part = re.sub(r'(^|[\s(\[])"', r"\1“", part)
        part = part.replace('"', "”")
        parts[i] = part
    return "".join(parts)


def relativize(doc, page_path):
    """Turn href="/x" and src="/x" into paths relative to the page's folder."""
    here = page_path if page_path.endswith("/") else posixpath.dirname(page_path) + "/"

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("//"):
            return m.group(0)
        target, frag = (url.split("#", 1) + [""])[:2]
        rel = posixpath.relpath(target, here) if target != here else "."
        if target.endswith("/") and not rel.endswith("/"):
            rel += "/"
        if rel == "./":
            rel = "./"
        return f'{attr}="{rel}{"#" + frag if frag else ""}"'
    return re.sub(r'\b(href|src)="(/[^"]*)"', fix, doc)


def write(path, doc):
    out = os.path.join(ROOT, path.lstrip("/"), "index.html") if path.endswith("/") else os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)


def redirect_page(old, new):
    rel = posixpath.relpath(new, old) + "/"  # relative so it also works under a sub-path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE_URL}{new}">
<meta http-equiv="refresh" content="0; url={rel}">
</head>
<body>
<p>This page has moved to <a href="{new}">{SITE_URL}{new}</a>.</p>
</body>
</html>
"""


def main():
    pages = []
    for dirpath, _, files in os.walk(SRC):
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            with open(os.path.join(dirpath, fn), encoding="utf-8") as f:
                text = f.read()
            m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->", text, re.S)
            if not m:
                raise ValueError(f"{fn}: missing meta comment")
            meta = json.loads(m.group(1))
            body = text[m.end():]
            if "—" in body or "–" in body:
                raise ValueError(f"{fn}: contains an em or en dash")
            doc = size_images(page(meta, smart_quotes(body)))
            write(meta["path"], doc if meta.get("absolute") else relativize(doc, meta["path"]))
            if meta.get("sitemap", True):
                pages.append(meta["path"])
            print("built", meta["path"])
    for old, new in REDIRECTS.items():
        write(old, relativize(redirect_page(old, new), old))
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc></url>\n" for p in sorted(pages))
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"{len(pages)} pages, {len(REDIRECTS)} redirects")


if __name__ == "__main__":
    main()
