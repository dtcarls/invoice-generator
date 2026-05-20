# PDF Invoice Generator — Implementation Plan

## Context

A single-user, self-hosted utility that produces PDF invoices for a small
business. It will be used rarely and only by the owner. Design priority is
**simplicity** over features: the smallest thing that works, deployable as
one Docker container, with persistent storage for settings (logo, address,
payment info) so they aren't re-entered every time.

Confirmed product decisions:

- **Interface:** Web UI (browser form) — no CLI.
- **Client directory:** Yes, save clients and pick from a dropdown.
- **Tax:** None. Subtotal == total.
- **Stack:** Python 3.12 + FastAPI + WeasyPrint + SQLite. See [ADR-0001](adr/0001-tech-stack.md).
- **Repeatable settings:** business address, email, phone, website, tax ID,
  default payment terms, default due-days, default currency, payment
  instructions, default footer notes, saved service/line-item presets.
- **Paper size:** US Letter (fixed, not configurable).
- **Payment status:** paid/unpaid toggle per invoice; toggling to paid
  auto-generates a receipt PDF.
- **Immutability:** finalized invoices cannot be edited. Mistakes are
  corrected by issuing a new invoice or a manual credit note. See
  [ADR-0008](adr/0008-immutable-invoices-and-auto-receipt.md).

Number formats:

- Invoice: `INV-{YYYY}-{MM}-{DD}-{NNNN}` — zero-padded; sequence resets
  per calendar day (e.g. `INV-2026-05-20-0001`).
- Receipt: `RCT-{YYYY}-{MM}-{DD}-{NNNN}` — based on the paid date; its own
  per-day sequence. Receipt PDF prints the corresponding invoice number for
  cross-reference.

## Deliverables

Implementing agent should produce, on branch
`claude/pdf-invoice-generator-plan-rqmOe`:

1. **Application code** (`app/`)
2. **Docker setup** (`Dockerfile`, `docker-compose.yml`)
3. **User documentation** (`docs/USAGE.md`, `docs/DEVELOPMENT.md`, `docs/BACKUP.md`)
4. **Tests** (`tests/`) — minimal smoke tests only.

The design docs (this file and the ADRs) are already in place.

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI + Jinja2 templates (server-rendered, no SPA) |
| PDF engine | WeasyPrint (HTML/CSS → PDF) |
| Storage | SQLite (single file, mounted volume) |
| Forms / UI | Plain HTML + minimal CSS (Pico.css or similar classless), HTMX only if needed |
| Container | Single Docker image, `docker compose up` to run |

Rationale captured in ADRs.

## Data Model (SQLite)

```
settings (single row, id=1)
  business_name TEXT
  address_line1 TEXT
  address_line2 TEXT
  city TEXT, region TEXT, postal_code TEXT, country TEXT
  email TEXT
  phone TEXT
  website TEXT
  tax_id TEXT                -- EIN / VAT (display only)
  logo_path TEXT             -- path under /data/logos/
  default_payment_terms TEXT -- e.g. "Net 30"
  default_due_days INTEGER   -- e.g. 30
  default_currency TEXT      -- e.g. "USD"
  payment_instructions TEXT  -- free text (ACH, Venmo, check-to, etc.)
  default_footer_notes TEXT  -- thank-you note, late-fee policy, etc.

clients
  id INTEGER PK
  name TEXT
  contact_name TEXT
  email TEXT
  address_line1 TEXT, address_line2 TEXT
  city TEXT, region TEXT, postal_code TEXT, country TEXT
  notes TEXT
  archived INTEGER DEFAULT 0

service_presets               -- saved line items for quick add
  id INTEGER PK
  description TEXT
  unit_price NUMERIC
  archived INTEGER DEFAULT 0

invoices
  id INTEGER PK
  number TEXT UNIQUE          -- INV-YYYY-MM-DD-NNNN
  issue_date DATE
  due_date DATE
  client_id INTEGER FK -> clients.id
  client_snapshot_json TEXT   -- frozen copy of client info at issue time
  business_snapshot_json TEXT -- frozen copy of settings at issue time
  currency TEXT
  notes TEXT                  -- per-invoice notes (overrides default footer if set)
  payment_instructions TEXT   -- per-invoice override
  total NUMERIC               -- denormalized for list view
  pdf_path TEXT               -- path under /data/pdfs/
  paid_at DATE                -- NULL if unpaid
  receipt_number TEXT UNIQUE  -- RCT-YYYY-MM-DD-NNNN, NULL until paid
  receipt_pdf_path TEXT       -- path under /data/receipts/, NULL until paid
  payment_method TEXT         -- optional free-text ("Check #1234", "ACH", "Venmo")
  created_at TIMESTAMP

invoice_items
  id INTEGER PK
  invoice_id INTEGER FK -> invoices.id
  position INTEGER            -- ordering
  description TEXT
  quantity NUMERIC
  unit_price NUMERIC
  line_total NUMERIC          -- quantity * unit_price
```

**Snapshots:** when an invoice is finalized, freeze the client and business
data into JSON columns so regenerating the PDF years later still produces
the same document even if you later change your address or the client
moves. See [ADR-0004](adr/0004-snapshot-client-business-data.md).

## Invoice & Receipt Numbering

`numbering.next_invoice_number(issue_date)`:

1. Compute prefix `INV-YYYY-MM-DD` from `issue_date`.
2. `SELECT COUNT(*) FROM invoices WHERE number LIKE 'INV-YYYY-MM-DD-%'` + 1.
3. Format the sequence as 4-digit zero-padded.
4. Insert with `UNIQUE` constraint on `number` — on rare race, retry once.

`numbering.next_receipt_number(paid_date)`:

- Same algorithm, prefix `RCT-YYYY-MM-DD`, counting existing
  `receipt_number` values for that date.

Contention is effectively zero in a single-user tool; the `UNIQUE`
constraints exist to protect against accidental double-submits.

## Pages / Routes (server-rendered)

| Route | Purpose |
|---|---|
| `GET /` | Dashboard: recent invoices, "New invoice" button |
| `GET /invoices` | List all invoices (filter by year/client) |
| `GET /invoices/new` | Create form: pick client, add line items, notes |
| `POST /invoices` | Finalize → assign number, render PDF, save |
| `GET /invoices/{id}` | View detail, re-download PDF, mark paid/unpaid |
| `GET /invoices/{id}/pdf` | Stream stored invoice PDF |
| `POST /invoices/{id}/mark-paid` | Set `paid_at`, optional `payment_method`, assign receipt number, render & store receipt PDF |
| `POST /invoices/{id}/mark-unpaid` | Clear `paid_at`, `receipt_number`, delete receipt PDF |
| `GET /invoices/{id}/receipt.pdf` | Stream stored receipt PDF (404 if unpaid) |
| `GET /clients` / `POST` / `GET /{id}/edit` / `POST /{id}` | Client CRUD |
| `GET /services` / `POST` / etc. | Service preset CRUD |
| `GET /settings` | Edit business profile + upload logo |
| `POST /settings` | Save settings; logo upload to `/data/logos/` |

No authentication — bind to `127.0.0.1` and run locally.
See [ADR-0005](adr/0005-no-auth-localhost-only.md).

## PDF Templates

Two Jinja2 templates rendered with WeasyPrint, both **US Letter**, sharing
a common CSS file:

- `app/templates/invoice_pdf.html` — header (logo + business snapshot),
  "Bill to" (client snapshot), line-item table, total, payment
  instructions, footer notes.
- `app/templates/receipt_pdf.html` — same layout, "RECEIPT" heading,
  "PAID" mark, paid date, payment method (if provided), and a
  cross-reference line like `For invoice INV-2026-05-20-0001`.

Logo embedded from `business_snapshot.logo_path` if present.

## Filesystem Layout (in container)

```
/app/                  # application code
/data/                 # mounted volume (persisted)
  invoices.db          # SQLite
  logos/
  pdfs/                # YYYY/INV-...pdf
  receipts/            # YYYY/RCT-...pdf
```

`docker-compose.yml` mounts `./data:/data` so deleting/recreating the
container doesn't lose data.

## Docker

- Base: `python:3.12-slim`
- System deps for WeasyPrint: `libpango-1.0-0`, `libpangoft2-1.0-0`
  (see WeasyPrint docs for the current list)
- `requirements.txt` pinned: fastapi, uvicorn, jinja2, weasyprint,
  sqlalchemy, python-multipart, pydantic
- `docker compose up` exposes port 8000 bound to `127.0.0.1`
- `ENTRYPOINT` runs an init step that creates tables if missing

## User Documentation to Produce

The implementing agent should add:

- `docs/USAGE.md` — how-to walkthrough (settings → client → invoice → mark paid → receipt).
- `docs/DEVELOPMENT.md` — running locally without Docker, running tests, code layout.
- `docs/BACKUP.md` — one page: stop container, copy `data/`, done.

## Critical Files to Create

```
Dockerfile
docker-compose.yml
requirements.txt
app/
  main.py                # FastAPI app, route registration
  db.py                  # SQLAlchemy engine + session
  models.py              # ORM models matching schema above
  schemas.py             # Pydantic request/response models
  numbering.py           # next_invoice_number / next_receipt_number helpers
  pdf.py                 # render_invoice_pdf, render_receipt_pdf → bytes, writes to disk
  routes/
    dashboard.py
    invoices.py
    clients.py
    services.py
    settings.py
  templates/
    base.html
    dashboard.html
    invoices_list.html
    invoice_form.html
    invoice_detail.html
    invoice_pdf.html     # invoice PDF template (separate from web layout)
    receipt_pdf.html     # receipt PDF template
    clients_list.html
    client_form.html
    services_list.html
    settings.html
  static/
    style.css
docs/
  USAGE.md
  DEVELOPMENT.md
  BACKUP.md
tests/
  test_numbering.py      # invoice + receipt sequence increment per day, reset next day
  test_pdf_render.py     # smoke: invoice + receipt produce non-empty PDF bytes
  test_mark_paid.py      # mark-paid assigns receipt number, generates receipt PDF
```

## Verification

After implementation, the coding agent should verify:

1. `docker compose up --build` starts cleanly, no errors in logs.
2. `curl http://127.0.0.1:8000/` returns 200.
3. Submit settings, upload a small PNG logo, create a client, create an
   invoice with 2 line items, download the PDF, open it — header shows
   logo + business info, "Bill to" shows client, line items + total
   correct, invoice number matches `INV-YYYY-MM-DD-0001` for today.
4. Create a second invoice the same day → number ends `-0002`.
5. Mark the first invoice as paid (payment method "Check #100") → list
   view shows "Paid"; receipt PDF downloadable, labeled
   `RCT-YYYY-MM-DD-0001`, references the invoice number.
6. Restart the container (`docker compose down && up`) → settings,
   clients, past invoices, and receipts persist.
7. `pytest` passes (numbering + PDF smoke tests + mark-paid).

## Out of Scope (explicit)

- Multi-user / authentication / RBAC
- Tax calculation (decided: none)
- Recurring invoices / scheduled sending
- Email delivery (just download the PDF and email manually)
- Payment processing integration (display instructions only)
- Internationalization / multi-currency conversion (single currency per invoice, no FX)
- Edit-after-finalize (finalized invoices are immutable; create a new one or a credit note manually)
- Cloud deployment, HTTPS, reverse proxy
