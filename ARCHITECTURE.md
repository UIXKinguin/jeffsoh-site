# ARCHITECTURE.md

How jeffsoh.com is built, and why. For visual and accessibility rules, see `DESIGN.md`.
For day-to-day editing steps, see `README.md`.

## The short version

No framework. Plain HTML pages, one hand-written CSS file, zero JavaScript, and a
~200-line Python script (`build.py`) that adds the shared header and footer. GitHub
Pages serves the built files; Cloudflare handles DNS.

| Layer | Choice | Why |
|---|---|---|
| Pages | Plain HTML | Nothing to learn or update; works in every browser |
| Styling | `assets/css/style.css` | Every rule is visible and intentional; no utility-class soup |
| Behavior | None (no JavaScript) | Fast, nothing to break, accessible by default |
| Build | `build.py` (Python standard library + Pillow) | Shared header/footer written once, not copied into 16 files |
| Fonts | Geist and Geist Mono in `assets/fonts/` | No third-party requests at page load |
| Hosting | GitHub Pages from `main`, custom domain `www.jeffsoh.com` | Free; publishing is a `git push` |
| DNS | Cloudflare | Free; registrar at cost |

## Folder map

```
src/                  page content (edit these)
  index.html          home
  my-work.html        work index
  my-work/*.html      case studies
  side-projects.html  research and projects index
  side-projects/*.html
  about-me.html, why-me.html, contact.html, 404.html
assets/
  css/style.css       the only stylesheet
  fonts/              Geist variable fonts (woff2)
  img/<page>/         WebP images, max 1600px wide
  og/                 link-preview images, one per page (generated)
  files/              resume PDF
build.py              the build script
tools/og_card.py      draws link-preview images (called by build.py)
tools/fonts/          Geist TTF used only to draw preview images
<path>/index.html     built pages (generated; do not edit by hand)
sitemap.xml, robots.txt, 404.html   generated
CNAME, .nojekyll      GitHub Pages settings
_source/              one-time Squarespace migration scripts (not served)
```

## Content fragments

Each file in `src/` holds only what is unique to that page. Its first line is a JSON
settings block inside an HTML comment, similar to the "front matter" used by site
generators such as Jekyll:

```html
<!-- {"title": "Terra", "description": "...", "path": "/my-work/terra/", "nav": "work"} -->
<div class="container"> ...page content... </div>
```

| Key | Meaning |
|---|---|
| `title` | Page title. The site name is appended automatically |
| `description` | Search and social-preview description |
| `path` | Public URL. A path ending in `/` is written to `<path>/index.html` |
| `nav` | Which header link is marked current: `projects` (labelled Research), `work`, `about`, `contact`, or `""` |
| `image` | Optional cover image shown on the page's link-preview card |
| `absolute` | Optional. Keep root-relative links (used by `404.html`, which can appear at any URL) |
| `sitemap` | Optional. `false` leaves the page out of `sitemap.xml` |

## The build pipeline

`python build.py` processes every fragment in `src/`, in this order:

1. **Read settings.** Parse the JSON comment at the top.
2. **Lint.** Stop the build if the text contains an em or en dash (a copy rule from `DESIGN.md`).
3. **`smart_quotes()`** turns straight quotes and apostrophes into curly ones, only in
   visible text, never inside tags or attributes.
4. **`og_card()`** draws a 1200x630 JPEG link-preview card for the page
   (`tools/og_card.py`): title, name and role, site address and, if the page sets
   `image`, that image on the right. LinkedIn and Slack show it when the link is shared.
5. **`page()`** wraps the fragment in the layout: `<head>` (title, description, canonical
   URL, Open Graph and Twitter card tags, theme color, favicon, font preload, stylesheet), then `header()`
   with `aria-current="page"` on the active link, `<main id="main">`, and `footer()`.
6. **`size_images()`** reads each image's real size with Pillow and adds `width`/`height`,
   so the layout doesn't jump while images load. It adds `loading="lazy"` to every image,
   except images marked `data-eager` (heroes and covers), which get `fetchpriority="high"`.
   **It stops the build if any image has no `alt` attribute.**
7. **`relativize()`** rewrites root-relative links (`/assets/...`) into relative ones
   (`../assets/...`), so the same files work at `www.jeffsoh.com/` or under any sub-path.
8. **`write()`** saves the page to `<path>/index.html`, which gives clean URLs like `/my-work/terra/`.

After the pages, the build writes:

- **Redirect pages** for old Squarespace URLs (the `REDIRECTS` table at the top of `build.py`),
  using `<meta http-equiv="refresh">` plus a canonical link, since GitHub Pages has no
  server-side redirects.
- **`sitemap.xml`** and **`robots.txt`** for search engines.

Both `src/` and the built pages are committed. GitHub Pages serves the built files as-is;
`.nojekyll` stops it from running its own Jekyll processor.

### Why regular expressions instead of an HTML parser?

The build edits HTML with a few small regular expressions. That is safe here only because
the input is our own hand-written fragments, and it keeps the script short and readable with
no extra dependencies. If the site ever accepts outside content, switch to a real parser.

## CSS patterns

The stylesheet is organized into numbered sections; see the contents comment at its top.

- **Design tokens.** Colors, type sizes, radii and widths are custom properties on `:root`.
  Change a value once and it updates everywhere.
- **Dark mode without a toggle.** `@media (prefers-color-scheme: dark)` redefines the color
  tokens. Components never need their own dark styles.
- **Fluid type.** `--step-*` sizes use `clamp(min, preferred, max)`, so headings scale
  smoothly instead of jumping at breakpoints.
- **Intrinsic grids.** `repeat(auto-fit, minmax(13rem, 1fr))` adds columns as space allows,
  so most components need no media queries.
- **`minmax(0, 1fr)`.** Lets a grid column shrink below its content's width. Without it,
  wide images forced horizontal scrolling on phones.
- **Stretched link.** On cards and row lists, the title link's `::after` covers the whole
  item, making it one click target and one link for screen readers.
  `:has(a:focus-visible)` draws the keyboard focus ring around the whole card.
- **Owl spacing.** `.prose > * + *` adds space only between siblings, giving text an even
  rhythm without stray margins at the edges.
- **Breakout widths.** Text is capped at `--text-col` (about 70 characters per line), while
  `.wide` figures, galleries and cards may use `--wide`.
- **Sticky contents.** Long case studies get a `position: sticky` sidebar on desktop and an
  inline list on phones.
- **Inline SVG diagrams.** The two research pages draw their diagrams as hand-written SVG
  in the HTML, with no images or libraries. Shapes and text use `.dg` classes that point at
  the color tokens, so the diagrams follow dark mode. Each figure holds a wide version
  (`.dg-wide`) and a stacked phone version (`.dg-tall`); a media query shows one, and
  `display: none` keeps the hidden one away from screen readers. Each SVG has
  `role="img"` and an `aria-label` that describes it in words.
- **Readable class names.** `.card`, `.gallery`, `.toc`, `.timeline` describe what a thing
  is, so the HTML reads like a document.

## Accessibility in the markup

- Landmarks (`header`, `nav`, `main`, `footer`), a skip link, one `h1` per page, and no
  skipped heading levels.
- `aria-current="page"` on the active nav link and in breadcrumbs.
- `.visually-hidden` headings give screen readers structure that sighted users don't need.
- Visible `:focus-visible` ring on every interactive element; reduced motion honored.
- All text colors pass contrast at 7:1 or better; targets are at least 44px tall.
- Every meaningful image has descriptive `alt` text; decorative card thumbnails use `alt=""`
  because the link text already names the project.

## Testing

Run before publishing larger changes:

- **Accessibility:** axe-core (WCAG 2.2 AA plus best practices) on every page, in light and
  dark mode, driven by `playwright-cli`.
- **Reflow:** check for horizontal overflow at 320, 375 and 768px widths.
- **Visual:** full-page screenshots at desktop and phone sizes.
- **Keyboard:** tab through a page; the skip link appears first and focus is always visible.

## Deployment

```
edit src/  ->  python build.py  ->  git commit  ->  git push  ->  GitHub Pages (about 1 minute)
```

- `CNAME` contains `www.jeffsoh.com`. GitHub issues the HTTPS certificate, and
  `jeffsoh.com` and the old `uixkinguin.github.io/jeffsoh-site` address redirect to it.
- Cloudflare DNS: four `A` and four `AAAA` records for the apex pointing at GitHub Pages,
  and `www` as a `CNAME` to `uixkinguin.github.io`, all set to "DNS only".

## The migration (`_source/`)

One-time scripts used to move off Squarespace, kept for reference:

1. `scrape.py` downloaded each page's HTML and full-size images.
2. `convert.py` / `convert2.py` (BeautifulSoup) walked each page's DOM in order and wrote
   clean draft HTML: text blocks, galleries and image captions, without Squarespace markup.
3. `optimize.py` (Pillow) converted images to WebP at most 1600px wide (50 MB to 5 MB).
4. Each draft was then rewritten by hand into `src/`, with new structure and alt text.

The raw downloads are excluded by `.gitignore`.

## Known trade-offs

- Editing a built `index.html` directly is lost on the next build. Always edit `src/`.
- A few fragments use inline `style=""` for one-off spacing.
- No JavaScript, so no interactive extras (for example, highlighting the current section
  in the contents sidebar).
