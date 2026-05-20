# ADR-0006: SQLite + Filesystem in a Single Mounted Volume

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

We need persistence for structured data (settings, clients, invoices,
line items) and binary blobs (logo image, generated PDFs). Backups must
be trivial.

## Decision

- **Structured data:** SQLite, one file at `/data/invoices.db`.
- **Binary blobs:** filesystem under `/data/logos/`, `/data/pdfs/`, and
  `/data/receipts/`. Database rows hold relative paths, not BLOBs.
- The whole `/data` directory is a single Docker volume bind-mounted
  from the host (`./data:/data`).

## Alternatives considered

- **Store PDFs as BLOBs in SQLite.** Keeps everything in one file, but
  SQLite is not ideal for many-MB blobs; viewing/checking a PDF
  externally would require an export step. Filesystem is friendlier.
- **Separate volumes for DB and files.** More config, no benefit at this
  scale.
- **Postgres in a sidecar.** See ADR-0001 — rejected as overkill.

## Consequences

- **Backup procedure:** stop the container, `cp -a data/ backup-YYYY-MM-DD/`.
  That's it.
- File paths are stored relative to `/data` so backups restore correctly
  even if the host path changes.
- The implementation must `mkdir -p` the subdirectories on startup if
  they don't exist (init step in the entrypoint).
- Not suitable for horizontal scaling — irrelevant for a single-user tool.
