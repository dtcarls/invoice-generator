import os
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Settings
from app.main import templates

DATA_DIR = os.environ.get("DATA_DIR", "/data")

router = APIRouter()


@router.get("/settings")
def settings_view(request: Request, db: Session = Depends(get_db), saved: Optional[str] = None):
    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "settings": settings, "saved": saved},
    )


@router.post("/settings")
async def settings_update(
    request: Request,
    db: Session = Depends(get_db),
    logo: Optional[UploadFile] = File(None),
):
    form = await request.form()

    settings = db.query(Settings).filter(Settings.id == 1).first()
    if not settings:
        settings = Settings(id=1)
        db.add(settings)

    # Handle logo upload
    logo_file: Optional[UploadFile] = form.get("logo")
    if logo_file and hasattr(logo_file, "filename") and logo_file.filename:
        logo_bytes = await logo_file.read()
        if logo_bytes:
            logos_dir = pathlib.Path(DATA_DIR) / "logos"
            logos_dir.mkdir(parents=True, exist_ok=True)
            filename = logo_file.filename
            dest = logos_dir / filename
            dest.write_bytes(logo_bytes)
            settings.logo_path = filename

    # Update text fields
    settings.business_name = form.get("business_name") or None
    settings.address_line1 = form.get("address_line1") or None
    settings.address_line2 = form.get("address_line2") or None
    settings.city = form.get("city") or None
    settings.region = form.get("region") or None
    settings.postal_code = form.get("postal_code") or None
    settings.country = form.get("country") or None
    settings.email = form.get("email") or None
    settings.phone = form.get("phone") or None
    settings.website = form.get("website") or None
    settings.tax_id = form.get("tax_id") or None
    settings.default_payment_terms = form.get("default_payment_terms") or None
    due_days_str = form.get("default_due_days")
    settings.default_due_days = int(due_days_str) if due_days_str and due_days_str.strip() else None
    settings.default_currency = form.get("default_currency") or None
    settings.payment_instructions = form.get("payment_instructions") or None
    settings.default_footer_notes = form.get("default_footer_notes") or None

    db.commit()

    return RedirectResponse(url="/settings?saved=1", status_code=303)
