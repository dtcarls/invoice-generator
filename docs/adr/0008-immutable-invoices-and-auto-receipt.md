# ADR-0008: Immutable Finalized Invoices; Auto-Generated Receipt on Mark-Paid

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

Invoices are accounting records. Once issued and sent to a client, their
content should not change — silently editing past invoices makes
reconciliation with payments and tax records impossible. Separately, the
owner asked for a receipt PDF to be generated when an invoice is marked
paid.

## Decision

- After `POST /invoices` finalizes an invoice (assigns a number, writes
  the PDF), no field on the invoice row may be edited **except** the
  payment-status fields: `paid_at`, `receipt_number`, `receipt_pdf_path`,
  `payment_method`.
- Line items are not editable after finalize.
- `POST /invoices/{id}/mark-paid` sets `paid_at` (defaults to today,
  user-overridable), optionally captures a `payment_method` free-text
  field, calls `next_receipt_number(paid_at)`, renders a receipt PDF
  from the existing invoice snapshots, and stores it under
  `/data/receipts/`.
- `POST /invoices/{id}/mark-unpaid` clears the payment fields and
  deletes the stored receipt PDF. This exists for correcting a
  mistakenly-marked invoice, not as a routine workflow.

To fix a substantive mistake in a finalized invoice (wrong amount, wrong
client), the owner issues a new invoice. A credit-note workflow is not
built in; "issue a corrective invoice" is the documented procedure.

## Alternatives considered

- **Editable finalized invoices.** Less friction in the moment, but
  rewrites accounting history. Rejected.
- **Receipt as a section appended to the invoice PDF.** Single document
  is simpler, but a separate receipt PDF is the conventional artifact
  and is easier to send to the client separately.

## Consequences

- The codebase enforces immutability in the route handlers — the form
  for `GET /invoices/{id}` does not present an "edit" button for
  finalized invoices.
- Marking an invoice paid is a one-click action that produces a
  downloadable receipt; the receipt cross-references the source invoice
  number for the client's records.
- `mark-unpaid` exists as an escape hatch but is intentionally a separate,
  explicit action.
