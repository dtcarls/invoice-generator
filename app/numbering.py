import datetime
from sqlalchemy import text


def next_invoice_number(db, issue_date: datetime.date) -> str:
    """
    Prefix: INV-YYYY-MM-DD
    Count existing invoices with that prefix, add 1, zero-pad to 4 digits.
    """
    prefix = f"INV-{issue_date.strftime('%Y-%m-%d')}"
    result = db.execute(
        text("SELECT COUNT(*) FROM invoices WHERE number LIKE :pattern"),
        {"pattern": f"{prefix}-%"},
    )
    count = result.scalar()
    seq = (count or 0) + 1
    return f"{prefix}-{seq:04d}"


def next_receipt_number(db, paid_date: datetime.date) -> str:
    """
    Prefix: RCT-YYYY-MM-DD
    Count existing receipt_number values with that prefix, add 1, zero-pad to 4 digits.
    """
    prefix = f"RCT-{paid_date.strftime('%Y-%m-%d')}"
    result = db.execute(
        text("SELECT COUNT(*) FROM invoices WHERE receipt_number LIKE :pattern"),
        {"pattern": f"{prefix}-%"},
    )
    count = result.scalar()
    seq = (count or 0) + 1
    return f"{prefix}-{seq:04d}"
