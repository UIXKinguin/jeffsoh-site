# Turn each Squarespace page into a clean draft HTML fragment (text blocks, images, buttons) in DOM order.
import json, os, re, urllib.request
from bs4 import BeautifulSoup, NavigableString

PAGES = json.load(open("site.json", encoding="utf-8")).keys()
KEEP = {"h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "strong", "em", "a", "br", "blockquote", "figcaption"}
os.makedirs("raw", exist_ok=True); os.makedirs("drafts", exist_ok=True)
imgmap = {}
for page in json.load(open("site.json", encoding="utf-8")).values():
    for c in page.get("content", []):
        if c["t"] == "img" and "file" in c: imgmap[c["src"]] = c["file"]

def fetch(path):
    fn = "raw/" + (path.strip("/").replace("/", "__") or "home") + ".html"
    if not os.path.exists(fn):
        req = urllib.request.Request("https://www.jeffsoh.com" + path, headers={"User-Agent": "Mozilla/5.0"})
        open(fn, "wb").write(urllib.request.urlopen(req, timeout=30).read())
    return open(fn, encoding="utf-8", errors="replace").read()

def clean(node):
    for t in node.find_all(True):
        if t.name not in KEEP:
            t.unwrap(); continue
        href = t.get("href")
        t.attrs = {"href": href} if (t.name == "a" and href) else {}
    s = str(node)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"<(p|h\d|li)>\s*</\1>", "", s)
    return s.strip()

for path in PAGES:
    try: raw = fetch(path)
    except Exception as e: print(path, e); continue
    soup = BeautifulSoup(raw, "html.parser")
    root = soup.find("main") or soup.find("article") or soup
    out = []
    for blk in root.select(".sqs-block, .user-items-list-item-container, li.list-item"):
        if blk.find_parent(class_="sqs-block") and "sqs-block" in (blk.get("class") or []): continue
        cls = " ".join(blk.get("class") or [])
        if "list-item" in cls:
            img = blk.find("img"); title = blk.select_one(".list-item-content__title"); desc = blk.select_one(".list-item-content__description"); btn = blk.find("a")
            out.append("<!-- list item -->")
            if img: out.append(f'<img src="{imgmap.get((img.get("data-src") or img.get("src","")).split("?")[0], img.get("data-src") or img.get("src"))}" alt="">')
            if title: out.append(f"<h3>{title.get_text(' ', strip=True)}</h3>")
            if desc: out.append(clean(desc))
            if btn: out.append(f'<a href="{btn.get("href")}">{btn.get_text(strip=True)}</a>')
            continue
        if "sqs-block-image" in cls or "image-block" in cls:
            img = blk.find("img")
            if img:
                src = (img.get("data-src") or img.get("src", "")).split("?")[0]
                cap = blk.select_one("figcaption, .image-caption")
                link = blk.find("a")
                out.append(f'<img src="{imgmap.get(src, src)}" alt="">' + (f' <!-- links to {link.get("href")} -->' if link else ""))
                if cap and cap.get_text(strip=True): out.append(f"<figcaption>{cap.get_text(' ', strip=True)}</figcaption>")
        elif "sqs-block-button" in cls:
            a = blk.find("a")
            if a: out.append(f'<a class="button" href="{a.get("href")}">{a.get_text(strip=True)}</a>')
        elif "sqs-block-html" in cls or "sqs-block-markdown" in cls:
            c = blk.select_one(".sqs-html-content") or blk
            h = clean(c)
            h = re.sub(r"^<div[^>]*>|</div>$", "", h)
            if h: out.append(h)
        elif "sqs-block-code" in cls:
            out.append("<!-- code block: " + blk.get_text(" ", strip=True)[:200] + " -->")
        elif "sqs-block-gallery" in cls or "gallery" in cls:
            for img in blk.find_all("img"):
                src = (img.get("data-src") or img.get("src", "")).split("?")[0]
                out.append(f'<img src="{imgmap.get(src, src)}" alt="">')
        elif "spacer" in cls or "horizontalrule" in cls:
            continue
        else:
            t = blk.get_text(" ", strip=True)
            if t: out.append(f"<!-- other block [{cls[:60]}]: {t[:200]} -->")
    slug = path.strip("/").replace("/", "__") or "home"
    open(f"drafts/{slug}.html", "w", encoding="utf-8").write("\n".join(out))
    print(path, len(out), "blocks")
