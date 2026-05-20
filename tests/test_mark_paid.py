import datetime
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(data_dir):
    from app.main import app
    from app.db import init_db, SessionLocal
    from app.models import Client, Invoice, InvoiceItem, Settings
    init_db()

    db = SessionLocal()
    # Seed settings
    existing_settings = db.query(Settings).filter(Settings.id == 1).first()
    if not existing_settings:
        settings = Settings(id=1, business_name="Test Biz", currency="USD", default_currency="USD")
        db.add(settings)

    # Seed client
    cl = Client(name="Test Client", email="tc@test.com")
    db.add(cl)
    db.flush()

    # Seed invoice
    today = datetime.date.today()
    inv = Invoice(
        number=f"INV-{today.strftime('%Y-%m-%d')}-TEST-0001",
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

    with TestClient(app) as c:
        c.invoice_id = invoice_id
        yield c


def test_mark_paid_assigns_receipt_number(client):
    invoice_id = client.invoice_id
    today = datetime.date.today().isoformat()
    resp = client.post(
        f"/invoices/{invoice_id}/mark-paid",
        data={"paid_at": today, "payment_method": "Check #100"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    from app.db import SessionLocal
    from app.models import Invoice
    db = SessionLocal()
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

    from app.db import SessionLocal
    from app.models import Invoice
    db = SessionLocal()
    inv = db.get(Invoice, invoice_id)
    assert inv.paid_at is None
    assert inv.receipt_number is None
    db.close()
