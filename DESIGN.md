# DESIGN.md

The visual language of jeffsoh.com. Read this before changing any page or style.

## Design read

A personal UX/UI portfolio for hiring managers and recruiters. Minimal, readable and
modern, and easy to scan. Plain HTML and one stylesheet, no frameworks, no JavaScript.

Dials (taste-skill scale): variance 5, motion 2, density 3.

## Principles

1. **Content first.** The case studies are the product. Chrome stays quiet.
2. **One idea per section.** A short heading, a few paragraphs, then the evidence (screens, flows, sketches).
3. **Predictable navigation.** The same four links on every page, the current page marked, and a way back to the list and on to the next project at the end of every case study.
4. **Accessible by default.** WCAG 2.2 AA is the floor, not a goal.

## Tokens

All colors live in `assets/css/style.css` under `:root` and switch with `prefers-color-scheme`.

| Token | Light | Dark | Use | Contrast on bg |
|---|---|---|---|---|
| `--bg` | `#FFFFFF` | `#111113` | Page background | |
| `--surface` | `#F4F4F5` | `#1B1B1F` | Image wells, tags, quote block | |
| `--text` | `#18181B` | `#EDEDEF` | Body and headings | 17.7 / 16.1 |
| `--muted` | `#52525B` | `#A1A1AA` | Secondary text, captions, meta | 7.7 / 7.4 |
| `--border` | `#E4E4E7` | `#2E2E33` | Hairlines only (decorative) | |
| `--accent` | `#2F4BC9` | `#9DB0FF` | Links, focus ring, primary button | 7.1 / 9.1 |

One accent only. No gradients, no glows, no pure black or white text.

## Type

- **Geist** (variable 400-700) for everything; **Geist Mono** for small metadata only.
- Self-hosted in `assets/fonts/`, `font-display: swap`.
- Fluid scale with `clamp()`: body 1.0625rem, line height 1.65, measure 68ch max.
- Headings use weight and tight tracking, not huge sizes. Max two lines for any hero headline.

## Shape and space

- Radius: 12px for images and cards, 8px for buttons and tags. Nothing else is rounded.
- Spacing scale: 0.25 / 0.5 / 1 / 1.5 / 2 / 3 / 4 / 6 / 8 rem.
- Content width 72rem; text column 42rem; wide figures 60rem.
- Cards only where they group a link target (project cards). Elsewhere use space and hairlines.

## Components

- **Header:** wordmark left, nav right; nav moves under the wordmark below 640px. `aria-current="page"` on the active link.
- **Project card:** image, title, one-line summary, role tags. The whole card is one link.
- **Case study:** back link, title, lede, meta list (product, role, duration), cover, optional contents list, sections, next-project link.
- **Gallery:** auto-fit grid for phone screens; every image has alt text.
- **Buttons:** primary (accent fill, white text), secondary (text-color outline). Labels of three words or fewer.

## Accessibility rules (non-negotiable)

- Skip link, landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page, no skipped heading levels.
- Every meaningful image has alt text that says what it shows; decorative images use `alt=""`.
- Visible focus ring: 3px accent outline, 2px offset, on every interactive element.
- Targets at least 44px tall in the header and buttons (WCAG 2.5.8 needs 24px).
- Text contrast 4.5:1 minimum (all tokens above clear 7:1).
- No content depends on hover or color alone. Links in body text are underlined.
- Reflows at 320px wide with no horizontal scrolling; works at 200% zoom.
- Motion limited to short color/transform transitions, disabled under `prefers-reduced-motion`.
- Links never open new tabs.

## Copy rules

- Plain, specific language. No em dashes or en dashes; use a hyphen, comma or period.
- The case-study text is Jeffrey's own writing; keep his voice when editing.
