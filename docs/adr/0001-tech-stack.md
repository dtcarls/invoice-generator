# ADR-0001: Tech Stack — Python + FastAPI + WeasyPrint + SQLite

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

We need a small, locally-run web app that renders PDF invoices for a
single user. It must be containerizable and trivial to deploy, the data
store must be a single file we can back up by copying, and the PDF engine
should produce a clean A-grade document from a styled HTML template.
Maintenance budget is near zero — fewer moving parts is better.

## Decision

- **Language:** Python 3.12.
- **Web framework:** FastAPI with Jinja2 server-rendered templates.
- **PDF engine:** WeasyPrint (HTML/CSS → PDF).
- **Storage:** SQLite via SQLAlchemy.

## Alternatives considered

- **Node.js + Puppeteer / Playwright.** Most flexible CSS rendering, but
  drags in headless Chromium — ~300–400 MB image, sandbox/seccomp
  considerations, and more moving parts than this tool warrants.
- **Python + ReportLab.** No system-library dependency, but layout is
  canvas-style imperative code. More code, less readable templates.
- **Postgres / MySQL.** Overkill for a single-user, low-volume tool. Adds
  a second container, networking, and credentials to manage.

## Consequences

- Small image (~200 MB on `python:3.12-slim` with Pango libs).
- Templates are plain HTML + CSS — easy to tweak the invoice layout.
- Backup = copy one `.db` file plus two folders.
- Requires Pango/Cairo system packages in the Docker image (one-line
  apt install).
- Not suited to multi-user or high-write workloads — explicitly out of
  scope.
