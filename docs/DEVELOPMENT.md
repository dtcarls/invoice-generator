# Invoice Generator — Development Guide

---

## Running Without Docker

### 1. Set Up a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the Data Directory

```bash
mkdir -p data/logos data/pdfs data/receipts
```

### 3. Start the Dev Server

```bash
DATA_DIR=./data uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000. The `--reload` flag restarts the server automatically when source files change.

---

## Running Tests

Install the test dependencies (if not already installed):

```bash
pip install pytest httpx
```

Run all tests:

```bash
pytest tests/ -v
```

Tests use isolated temporary SQLite databases so they never touch your real `data/` directory.

---

## Code Layout

```
app/
├── __init__.py
├── main.py              # FastAPI app + lifespan (startup/shutdown)
├── db.py                # SQLAlchemy engine, SessionLocal, init_db()
├── models.py            # ORM models: Settings, Client, Invoice, InvoiceItem, ServicePreset
├── numbering.py         # next_invoice_number() and next_receipt_number()
├── pdf.py               # render_invoice_pdf() and render_receipt_pdf() via WeasyPrint
├── schemas.py           # Pydantic schemas (reserved for future API use)
├── templates_config.py  # Shared Jinja2Templates instance
├── routes/
│   ├── dashboard.py     # GET /
│   ├── invoices.py      # CRUD + mark-paid/unpaid + PDF download
│   ├── clients.py       # CRUD for clients
│   ├── services.py      # CRUD for service presets
│   └── settings.py      # GET/POST /settings
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── invoice_form.html
│   ├── invoice_detail.html
│   ├── invoice_pdf.html   # WeasyPrint source for invoice PDFs
│   ├── receipt_pdf.html   # WeasyPrint source for receipt PDFs
│   └── ...
└── static/
    └── style.css
```

### Key Design Decisions

- **Snapshot pattern**: When an invoice is created, the client and business details are snapshotted as JSON in `client_snapshot_json` and `business_snapshot_json`. This ensures PDFs remain accurate even if client or business data changes later.
- **Sequential numbering**: Invoice numbers follow the format `INV-YYYY-MM-DD-NNNN`. The sequence resets each day.
- **Auto-receipt**: Marking an invoice as paid automatically generates a receipt PDF (`RCT-YYYY-MM-DD-NNNN`).
- **No auth**: The app is designed for localhost-only use. Do not expose it on a public network.

---

## Adding a New Route

1. Create or open the relevant router in `app/routes/`.
2. Define a handler using `@router.get(...)` or `@router.post(...)`.
3. Use `Depends(get_db)` to get a database session.
4. Use `templates.TemplateResponse(...)` (imported from `app.templates_config`) to render HTML.
5. Include the router in `app/main.py` if it is a new file:

```python
from app.routes import my_new_module
app.include_router(my_new_module.router)
```

### Example Route

```python
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Invoice
from app.templates_config import templates

router = APIRouter()

@router.get("/invoices/summary")
def invoice_summary(request: Request, db: Session = Depends(get_db)):
    total = db.query(Invoice).count()
    return templates.TemplateResponse(
        "summary.html",
        {"request": request, "total": total},
    )
```

---

## Environment Variables

| Variable   | Default  | Description                              |
|------------|----------|------------------------------------------|
| `DATA_DIR` | `/data`  | Directory for the SQLite DB and PDF files |

---

## System Dependencies (for WeasyPrint)

WeasyPrint requires several system libraries for PDF rendering. They are installed automatically in the Docker image (see `Dockerfile`). When running without Docker, install them with:

```bash
# Debian / Ubuntu
sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info fonts-liberation
```
