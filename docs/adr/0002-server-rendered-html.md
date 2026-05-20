# ADR-0002: Server-Rendered HTML, No SPA

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

The UI is a handful of forms (settings, client CRUD, invoice create/list)
used by one person, occasionally. A single-page-app framework would add a
build step, a JS toolchain, and ongoing dependency churn for no real
user-facing benefit at this scale.

## Decision

Render pages on the server with Jinja2 templates. Sprinkle in HTMX only
if a specific interaction (e.g. "add line item" without full page reload)
clearly benefits from it.

## Alternatives considered

- **React / Vue / Svelte SPA + JSON API.** Idiomatic for larger apps, but
  needs a Node build pipeline, bundling, and a separation between
  frontend and backend that costs more than it earns here.
- **Pure HTML forms only, no HTMX.** Workable. HTMX is allowed but not
  required — it's a small ergonomic upgrade for one or two interactions.

## Consequences

- No build step. `docker compose up` is the entire dev loop.
- Smaller dependency surface; nothing to upgrade quarterly.
- Slightly less interactive UI (full page reloads on most submits) —
  acceptable for a tool used a few times a month.
