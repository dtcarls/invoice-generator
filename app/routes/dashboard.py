from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Invoice
from app.templates_config import templates

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    recent_invoices = (
        db.query(Invoice)
        .order_by(Invoice.created_at.desc())
        .limit(10)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "recent_invoices": recent_invoices},
    )
