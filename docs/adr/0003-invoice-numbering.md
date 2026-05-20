# ADR-0003: Invoice and Receipt Numbering Format

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

The owner specified the invoice number format:
`INV-{YEAR}-{Month-number}-{day-number}-0001`, with the 4-digit suffix
incrementing if more than one invoice is issued on the same date. We also
need a parallel scheme for receipts.

## Decision

- **Invoice number:** `INV-YYYY-MM-DD-NNNN`, zero-padded month/day,
  sequence resets per calendar day based on the invoice's `issue_date`.
- **Receipt number:** `RCT-YYYY-MM-DD-NNNN`, same algorithm, based on the
  invoice's `paid_at` date. Sequence is independent of the invoice's
  sequence. The receipt PDF cross-references the source invoice number.
- Sequence assignment computes `COUNT(*) + 1` of existing rows whose
  number starts with the day's prefix; the `UNIQUE` constraint on the
  number column guards against accidental double-submits.

Zero-padding (e.g. `05`, not `5`) is chosen so numbers sort
lexicographically in the same order as chronologically.

## Alternatives considered

- **Global monotonic counter (`INV-0001`, `INV-0002`, …).** Simpler but
  loses the at-a-glance date context the owner wanted.
- **Receipts share the invoice number with a suffix
  (e.g. `INV-…-0001-R`).** Compact, but conflates two distinct events.
  Receipts are issued on payment day, which may be much later than the
  invoice date; giving receipts their own date-based number captures
  when payment actually arrived.

## Consequences

- Numbers are human-readable and sort correctly.
- The number reveals how often invoices are issued — acceptable for a
  single-user tool.
- Both invoice and receipt numbers are unique across the database (via
  `UNIQUE` constraints).
