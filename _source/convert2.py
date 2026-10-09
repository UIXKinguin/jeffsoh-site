# Second pass: walk the DOM in order so gallery and section-background images are kept in place.
import json, re
from bs4 import BeautifulSoup, Tag
from convert import clean, imgmap, fetch  # reuse helpers (re-runs convert.py once on import)

def walk(node, out, seen):
    for ch in node.children:
        if not isinstance(ch, Tag): continue
        cls = " ".join(ch.get("class") or [])
        if "sqs-html-content" in cls:
            h = clean(ch); h = re.sub(r"^<div[^>]*>|</div>$", "", h)
            if h: out.append(h)
            continue
        if ch.name == "img":
            src = (ch.get("data-src") or ch.get("src", "")).split("?")[0]
            if not src or src in seen or "squarespace" not in src: continue
            seen.add(src)
            kind = "bg" if ch.find_parent(class_="section-background") else ("gallery" if ch.find_parent(class_=re.compile("gallery")) else "img")
            link = ch.find_parent("a")
            out.append(f'<img data-kind="{kind}" src="{imgmap.get(src, src)}" alt="">' + (f' <!-- links to {link.get("href")} -->' if link and link.get("href") else ""))
            continue
        if "sqs-block-button" in cls or "list-item-content__button" in cls:
            a = ch.find("a")
            if a: out.append(f'<a class="button" href="{a.get("href")}">{a.get_text(strip=True)}</a>')
            continue
        if any(k in cls for k in ("list-item-content__title", "list-item-content__description", "image-caption", "portfolio-title")):
            t = clean(ch)
            if t: out.append(f'<!-- {cls.split()[0]} --> ' + t)
            continue
        walk(ch, out, seen)

for path in json.load(open("site.json", encoding="utf-8")):
    try: raw = fetch(path)
    except Exception: continue
    soup = BeautifulSoup(raw, "html.parser")
    root = soup.find("main") or soup.find("article") or soup
    out = []; walk(root, out, set())
    slug = path.strip("/").replace("/", "__") or "home"
    open(f"drafts/{slug}.html", "w", encoding="utf-8").write("\n".join(out))
    print(path, len(out), "blocks,", sum(1 for x in out if x.startswith("<img")), "imgs")
