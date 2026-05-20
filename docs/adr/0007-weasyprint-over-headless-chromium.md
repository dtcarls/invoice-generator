# ADR-0007: WeasyPrint over Headless Chromium for PDF Rendering

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

We need to render HTML/CSS to PDF. Two mainstream choices:

1. **WeasyPrint** — Python library; renders via Cairo/Pango. Subset of
   modern CSS but solid coverage of layout, tables, and `@page`.
2. **Headless Chromium** (Puppeteer / Playwright) — full browser
   rendering, near-perfect CSS support.

## Decision

Use WeasyPrint.

## Alternatives considered

- **Headless Chromium.** Best fidelity, but the Docker image balloons to
  ~400 MB, adds a sandboxed Chromium process, and brings GPU/seccomp
  concerns we don't want to think about for a tool that prints a
  table-with-a-header-and-totals.
- **ReportLab.** Canvas-style imperative API. More code, harder to tweak
  the invoice layout. Better suited to programmatic forms than
  template-driven documents.
- **wkhtmltopdf.** Old QtWebKit fork; project is dormant and Debian
  removed it from default repos.

## Consequences

- ~10× smaller image than Chromium-based options.
- Requires a few system packages (Pango, Cairo, GDK-Pixbuf) — one apt
  line in the Dockerfile.
- Some CSS features won't work (e.g. CSS Grid is partial as of recent
  versions). The invoice template should stick to flexbox + tables,
  which are well-supported.
- Logo embedding works via standard `<img src="file:///data/logos/...">`
  references; WeasyPrint resolves local file URIs at render time.
