from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Invoice, Client
from app.main import templates

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    recent_invoices = (
        db.query(Invoice, Client)
        .outerjoin(Client, Invoice.client_id == Client.id)
        .order_by(Invoice.created_at.desc())
        .limit(10)
        .all()
    )

    # Build a list of dicts for template convenience
    invoice_rows = []
    for invoice, client in recent_invoices:
        invoice_rows.append({"invoice": invoice, "client": client})

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "recent_invoices": invoice_rows},
    )
