import datetime
from app.numbering import next_invoice_number, next_receipt_number
from app.models import Invoice


def test_first_invoice_number(db):
    d = datetime.date(2026, 5, 20)
    assert next_invoice_number(db, d) == "INV-2026-05-20-0001"


def test_second_invoice_same_day(db):
    d = datetime.date(2026, 5, 20)
    inv = Invoice(number="INV-2026-05-20-0001", issue_date=d, due_date=d, currency="USD", total=0)
    db.add(inv)
    db.commit()
    assert next_invoice_number(db, d) == "INV-2026-05-20-0002"


def test_invoice_sequence_resets_next_day(db):
    d1 = datetime.date(2026, 5, 20)
    d2 = datetime.date(2026, 5, 21)
    inv = Invoice(number="INV-2026-05-20-0001", issue_date=d1, due_date=d1, currency="USD", total=0)
    db.add(inv)
    db.commit()
    assert next_invoice_number(db, d2) == "INV-2026-05-21-0001"


def test_first_receipt_number(db):
    d = datetime.date(2026, 6, 1)
    assert next_receipt_number(db, d) == "RCT-2026-06-01-0001"


def test_second_receipt_same_day(db):
    d = datetime.date(2026, 6, 1)
    inv = Invoice(
        number="INV-2026-06-01-0001",
        issue_date=d,
        due_date=d,
        currency="USD",
        total=0,
        receipt_number="RCT-2026-06-01-0001",
    )
    db.add(inv)
    db.commit()
    assert next_receipt_number(db, d) == "RCT-2026-06-01-0002"
