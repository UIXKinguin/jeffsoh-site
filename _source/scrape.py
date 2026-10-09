# Pull text and images from the current Squarespace site into _source/ for the rebuild.
import json, re, os, urllib.request, html
from html.parser import HTMLParser

BASE = "https://www.jeffsoh.com"
PAGES = ["/", "/my-work", "/my-work/myrelocation-guide", "/my-work/terra", "/my-work/venmo-groups",
         "/my-work/lost-ark-forums", "/my-work/penn-state-eats", "/my-work/zeit-website", "/general-2",
         "/about-me", "/why-me", "/contact", "/ev-battery-failure-prediction-agent", "/automated-trading-bot"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

class P(HTMLParser):
    BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "blockquote", "figcaption"}
    def __init__(self):
        super().__init__(); self.out = []; self.stack = []; self.buf = None; self.skip = 0; self.in_main = 0
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("script", "style", "noscript"): self.skip += 1
        if tag in ("main", "article") or a.get("id") == "page": self.in_main += 1
        if not self.in_main or self.skip: return
        if tag in self.BLOCK and self.buf is None: self.buf = [tag, ""]
        if tag == "img":
            src = a.get("data-src") or a.get("src") or ""
            if "squarespace-cdn" in src or "static1.squarespace" in src:
                self.out.append({"t": "img", "src": src.split("?")[0], "alt": a.get("alt", "")})
        if tag == "a" and a.get("href"):
            self.out.append({"t": "link", "href": a["href"]})
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"): self.skip -= 1
        if tag in ("main", "article") and self.in_main: self.in_main -= 1
        if self.buf and tag == self.buf[0]:
            txt = re.sub(r"\s+", " ", self.buf[1]).strip()
            if txt: self.out.append({"t": tag, "text": txt})
            self.buf = None
    def handle_data(self, d):
        if self.buf is not None and not self.skip: self.buf[1] += d

os.makedirs("images", exist_ok=True)
site = {}
for path in PAGES:
    try:
        raw = get(BASE + path).decode("utf-8", "replace")
    except Exception as e:
        site[path] = {"error": str(e)}; continue
    p = P(); p.feed(raw)
    title = re.search(r"<title>(.*?)</title>", raw, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', raw)
    site[path] = {"title": html.unescape(title.group(1).strip()) if title else "",
                  "description": html.unescape(desc.group(1)) if desc else "", "content": p.out}
    for item in p.out:
        if item["t"] == "img":
            name = re.sub(r"[^A-Za-z0-9._-]", "_", item["src"].rsplit("/", 1)[-1]) or "img"
            slug = path.strip("/").replace("/", "__") or "home"
            fn = f"images/{slug}__{name}"
            item["file"] = fn
            if not os.path.exists(fn):
                try:
                    open(fn, "wb").write(get(item["src"] + "?format=2500w"))
                except Exception as e:
                    item["error"] = str(e)
json.dump(site, open("site.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for k, v in site.items():
    c = v.get("content", [])
    print(k, v.get("error", ""), "blocks=%d imgs=%d" % (len([x for x in c if x["t"] not in ("img", "link")]), len([x for x in c if x["t"] == "img"])))
