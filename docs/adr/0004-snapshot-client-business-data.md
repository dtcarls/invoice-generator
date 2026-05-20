# ADR-0004: Snapshot Client and Business Data into Each Invoice

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

Business settings (address, logo path, payment instructions) and client
records (address, contact name) change over time. An invoice issued in
2026 must continue to render with the address that was current in 2026,
even if the business relocates or the client moves in 2028.

## Decision

When an invoice is finalized, store a JSON snapshot of the business
settings and the client record on the invoice row
(`business_snapshot_json`, `client_snapshot_json`). The PDF template
reads from these snapshots, never from the live `settings` / `clients`
tables.

The same snapshot is used when rendering the receipt PDF, so a receipt
generated months after the invoice still matches it.

## Alternatives considered

- **Render from live data on every PDF regeneration.** Simpler at write
  time, but rewrites history when settings change. Unacceptable for
  invoices, which are accounting records.
- **Versioned settings tables (effective-dated rows).** More flexible but
  much more code. Overkill for a single user.

## Consequences

- A small amount of duplicated data per invoice (~1 KB JSON). Negligible
  at this scale.
- Editing settings or a client record never alters the appearance of
  past invoices or receipts.
- Implementation note: snapshot fields by name into a dict and
  `json.dumps()` it; do not pickle.
