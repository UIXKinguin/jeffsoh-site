# Resize and convert scraped images to WebP under assets/img/<page>/, keeping a name map for the build.
import os, re, json
from PIL import Image, ImageOps
SRC = "_source/images"; DST = "assets/img"; MAXW = 1600
m = {}
for fn in sorted(os.listdir(SRC)):
    slugs = ["my-work__myrelocation-guide", "my-work__terra", "my-work__venmo-groups", "my-work__lost-ark-forums",
             "my-work__penn-state-eats", "my-work__zeit-website", "my-work", "general-2", "about-me", "why-me", "home"]
    pre = next(x for x in slugs if fn.startswith(x + "__"))
    sub, name = pre.replace("my-work__", ""), fn[len(pre) + 2:]
    base = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(name)[0].lower().replace("_e2_80_93", "")).strip("-")
    out_dir = os.path.join(DST, sub); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, base + ".webp")
    try:
        im = Image.open(os.path.join(SRC, fn)); im = ImageOps.exif_transpose(im)
        if im.mode in ("P", "LA"): im = im.convert("RGBA")
        if im.mode not in ("RGB", "RGBA"): im = im.convert("RGB")
        if im.width > MAXW: im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        im.save(out, "WEBP", quality=80, method=6)
        m["_source/images/" + fn] = {"path": out.replace("\\", "/"), "w": im.width, "h": im.height}
    except Exception as e:
        print("FAIL", fn, e)
json.dump(m, open("_source/imgmap.json", "w"), indent=1)
print(len(m), "images")
