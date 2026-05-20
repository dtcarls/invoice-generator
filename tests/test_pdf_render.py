import datetime
import pytest
from unittest.mock import MagicMock
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env():
    return Environment(loader=FileSystemLoader("app/templates"))


def make_invoice(number="INV-2026-05-20-0001"):
    inv = MagicMock()
    inv.number = number
    inv.issue_date = datetime.date(2026, 5, 20)
    inv.due_date = datetime.date(2026, 6, 19)
    inv.currency = "USD"
    inv.total = 500.00
    inv.notes = ""
    inv.payment_instructions = "Pay via ACH"
    inv.paid_at = None
    inv.receipt_number = None
    return inv


def make_items():
    item = MagicMock()
    item.description = "Consulting services"
    item.quantity = 10
    item.unit_price = 50.00
    item.line_total = 500.00
    return [item]


BUSINESS = {
    "business_name": "Acme Corp",
    "address_line1": "123 Main St",
    "city": "Springfield",
    "region": "IL",
    "postal_code": "62701",
    "country": "US",
    "email": "billing@acme.com",
    "phone": "555-1234",
    "website": "",
    "logo_path": None,
    "payment_instructions": "Pay via ACH",
    "default_footer_notes": "Thank you!",
}
CLIENT = {
    "name": "Client Co",
    "contact_name": "Jane Doe",
    "address_line1": "456 Oak Ave",
    "city": "Shelbyville",
    "region": "IL",
    "postal_code": "62702",
    "country": "US",
    "email": "jane@client.co",
}


def test_invoice_pdf_renders(jinja_env, data_dir):
    from app.pdf import render_invoice_pdf
    invoice = make_invoice()
    items = make_items()
    pdf_bytes = render_invoice_pdf(invoice, items, BUSINESS, CLIENT, jinja_env)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"


def test_receipt_pdf_renders(jinja_env, data_dir):
    from app.pdf import render_receipt_pdf
    invoice = make_invoice()
    invoice.paid_at = datetime.date(2026, 6, 1)
    invoice.receipt_number = "RCT-2026-06-01-0001"
    invoice.payment_method = "Check #100"
    pdf_bytes = render_receipt_pdf(invoice, BUSINESS, CLIENT, jinja_env)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"
