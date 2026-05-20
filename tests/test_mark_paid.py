import datetime
import os
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """
    Provide a seeded TestClient backed by a fresh per-test SQLite database.

    Each test gets its own DATA_DIR with a clean invoices.db so the FastAPI
    lifespan init_db() picks it up correctly and there is no data leakage.
    """
    import app.db as app_db_module
    import app.main as app_main_module
    import app.pdf as app_pdf_module
    import app.routes.invoices as invoices_module
    import app.routes.settings as settings_module

    with tempfile.TemporaryDirectory() as test_data_dir:
        for sub in ("logos", "pdfs", "receipts"):
            os.makedirs(os.path.join(test_data_dir, sub), exist_ok=True)

        # Point DATA_DIR to our isolated temp directory so init_db() creates
        # invoices.db there, and PDF/receipt files land in the right place.
        os.environ["DATA_DIR"] = test_data_dir
        # Patch the DATA_DIR constant in modules that cache it at import time
        app_main_module.DATA_DIR = test_data_dir
        app_pdf_module.DATA_DIR = test_data_dir
        invoices_module.DATA_DIR = test_data_dir
        settings_module.DATA_DIR = test_data_dir

        from app.main import app
        from app.models import Client, Invoice, InvoiceItem, Settings

        # Use TestClient as context manager — this triggers the lifespan
        # which calls init_db() (now pointed at our test_data_dir).
        with TestClient(app) as tc:
            db = app_db_module.SessionLocal()

            # Seed settings
            settings = Settings(id=1, business_name="Test Biz", default_currency="USD")
            db.add(settings)

            # Seed client
            cl = Client(name="Test Client", email="tc@test.com")
            db.add(cl)
            db.flush()

            # Seed invoice
            today = datetime.date.today()
            inv = Invoice(
                number=f"INV-{today.strftime('%Y-%m-%d')}-0001",
                issue_date=today,
                due_date=today,
                client_id=cl.id,
                client_snapshot_json='{"name": "Test Client", "email": "tc@test.com"}',
                business_snapshot_json='{"business_name": "Test Biz", "logo_path": null}',
                currency="USD",
                total=100.00,
            )
            db.add(inv)
            db.flush()
            item = InvoiceItem(
                invoice_id=inv.id,
                position=1,
                description="Test service",
                quantity=1,
                unit_price=100.00,
                line_total=100.00,
            )
            db.add(item)
            db.commit()
            invoice_id = inv.id
            db.close()

            tc.invoice_id = invoice_id
            yield tc


def test_mark_paid_assigns_receipt_number(client):
    invoice_id = client.invoice_id
    today = datetime.date.today().isoformat()
    resp = client.post(
        f"/invoices/{invoice_id}/mark-paid",
        data={"paid_at": today, "payment_method": "Check #100"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    import app.db as app_db_module
    from app.models import Invoice
    db = app_db_module.SessionLocal()
    inv = db.get(Invoice, invoice_id)
    assert inv.paid_at is not None
    assert inv.receipt_number is not None
    assert inv.receipt_number.startswith("RCT-")
    assert inv.receipt_pdf_path is not None
    db.close()


def test_mark_unpaid_clears_receipt(client):
    invoice_id = client.invoice_id
    today = datetime.date.today().isoformat()
    # First mark paid
    client.post(
        f"/invoices/{invoice_id}/mark-paid",
        data={"paid_at": today, "payment_method": "ACH"},
        follow_redirects=True,
    )
    # Then mark unpaid
    resp = client.post(f"/invoices/{invoice_id}/mark-unpaid", follow_redirects=True)
    assert resp.status_code == 200

    import app.db as app_db_module
    from app.models import Invoice
    db = app_db_module.SessionLocal()
    inv = db.get(Invoice, invoice_id)
    assert inv.paid_at is None
    assert inv.receipt_number is None
    db.close()
