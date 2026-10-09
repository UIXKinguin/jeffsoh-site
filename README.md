# jeffsoh.com

Jeffrey Oh's portfolio: plain HTML and one CSS file, no framework and no JavaScript.
Free to host on GitHub Pages, Cloudflare Pages or Netlify.

## Edit a page

1. Edit the page's fragment in `src/` (for example `src/my-work/terra.html`).
   The first line is a JSON comment with the page title, description, URL path and
   active nav item.
2. Rebuild:

   ```bash
   pip install pillow
   python build.py
   ```

   The build wraps each fragment in the shared header and footer, adds image sizes and
   lazy loading, converts straight quotes to curly ones, makes links relative, and writes
   `<path>/index.html`, `sitemap.xml`, `robots.txt` and redirect pages for old URLs.
   It stops with an error if an image has no `alt` or the text contains an em or en dash.
3. Preview:

   ```bash
   python -m http.server 8765
   ```

   Then open http://localhost:8765.

Commit both `src/` and the built HTML. Hosts serve the built files as they are, with no
build step.

## Add a case study

Copy an existing fragment in `src/my-work/`, change the meta line and content, add
images under `assets/img/<project>/` (WebP, at most 1600px wide), add a card to
`src/my-work.html`, and update the previous case study's "Next case study" link.

## Layout

| Path | What it is |
|---|---|
| `src/` | Page content (edit these) |
| `assets/css/style.css` | The only stylesheet; tokens at the top |
| `assets/img/`, `assets/fonts/` | Images (WebP) and self-hosted Geist fonts |
| `build.py` | The build script |
| `DESIGN.md` | Design system and accessibility rules |
| `_source/` | Scripts used to migrate content from Squarespace (not served) |
| `.claude/skills/` | Design skills for Claude Code sessions in this repo |

## Accessibility

The site targets WCAG 2.2 AA. See `DESIGN.md` for the rules. Before publishing changes,
check pages with an automated tool such as axe, and tab through them with a keyboard.
