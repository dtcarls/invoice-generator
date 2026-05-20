import json
import datetime
import pathlib
import os
from typing import Optional, List

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Invoice, InvoiceItem, Client, Settings
from app.numbering import next_invoice_number, next_receipt_number
from app.pdf import render_invoice_pdf, render_receipt_pdf
from app.main import templates

DATA_DIR = os.environ.get("DATA_DIR", "/data")

router = APIRouter()


def client_to_dict(client: Client) -> dict:
    return {
        "id": client.id,
        "name": client.name,
        "contact_name": client.contact_name,
        "email": client.email,
        "address_line1": client.address_line1,
        "address_line2": client.address_line2,
        "city": client.city,
        "region": client.region,
        "postal_code": client.postal_code,
        "country": client.country,
        "notes": client.notes,
    }


def settings_to_dict(settings: Settings) -> dict:
    return {
        "id": settings.id,
        "business_name": settings.business_name,
        "address_line1": settings.address_line1,
        "address_line2": settings.address_line2,
        "city": settings.city,
        "region": settings.region,
        "postal_code": settings.postal_code,
        "country": settings.country,
        "email": settings.email,
        "phone": settings.phone,
        "website": settings.website,
        "tax_id": settings.tax_id,
        "logo_path": settings.logo_path,
        "default_payment_terms": settings.default_payment_terms,
        "default_due_days": settings.default_due_days,
        "default_currency": settings.default_currency,
        "payment_instructions": settings.payment_instructions,
        "default_footer_notes": settings.default_footer_notes,
    }


@router.get("/invoices")
def invoices_list(
    request: Request,
    db: Session = Depends(get_db),
    year: Optional[int] = None,
    client_id: Optional[int] = None,
):
    query = db.query(Invoice)
    if year:
        query = query.filter(Invoice.issue_date >= datetime.date(year, 1, 1)).filter(
            Invoice.issue_date <= datetime.date(year, 12, 31)
        )
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    invoices = query.order_by(Invoice.created_at.desc()).all()
    clients = db.query(Client).filter(Client.archived == 0).all()

    return templates.TemplateResponse(
        "invoices_list.html",
        {
            "request": request,
            "invoices": invoices,
            "clients": clients,
            "filter_year": year,
            "filter_client_id": client_id,
        },
    )


@router.get("/invoices/new")
def invoice_new(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Client).filter(Client.archived == 0).all()
    from app.models import ServicePreset
    presets = db.query(ServicePreset).filter(ServicePreset.archived == 0).all()
    settings = db.query(Settings).filter(Settings.id == 1).first()
    return templates.TemplateResponse(
        "invoice_form.html",
        {"request": request, "clients": clients, "presets": presets, "settings": settings},
    )


@router.post("/invoices")
async def invoice_create(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    client_id = int(form.get("client_id"))
    issue_date = datetime.date.fromisoformat(form.get("issue_date"))
    due_date = datetime.date.fromisoformat(form.get("due_date"))
    currency = form.get("currency", "USD")
    notes = form.get("notes") or None
    payment_instructions = form.get("payment_instructions") or None

    # Parse repeated item fields
    descriptions: List[str] = form.getlist("item_description[]")
    quantities: List[str] = form.getlist("item_quantity[]")
    unit_prices: List[str] = form.getlist("item_unit_price[]")

    # Build items and compute total
    items_data = []
    total = 0.0
    for i, (desc, qty_str, price_str) in enumerate(zip(descriptions, quantities, unit_prices)):
        if not desc.strip():
            continue
        qty = float(qty_str)
        unit_price = float(price_str)
        line_total = round(qty * unit_price, 2)
        total += line_total
        items_data.append({
            "position": i + 1,
            "description": desc.strip(),
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    total = round(total, 2)

    # Snapshots
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    settings = db.query(Settings).filter(Settings.id == 1).first()

    client_snapshot = client_to_dict(client)
    business_snapshot = settings_to_dict(settings) if settings else {}

    inv_number = next_invoice_number(db, issue_date)

    invoice = Invoice(
        number=inv_number,
        issue_date=issue_date,
        due_date=due_date,
        client_id=client_id,
        client_snapshot_json=json.dumps(client_snapshot),
        business_snapshot_json=json.dumps(business_snapshot),
        currency=currency,
        notes=notes,
        payment_instructions=payment_instructions,
        total=total,
    )
    db.add(invoice)
    db.flush()  # get invoice.id

    for item_data in items_data:
        item = InvoiceItem(invoice_id=invoice.id, **item_data)
        db.add(item)

    db.flush()

    # Render PDF
    pdf_bytes = render_invoice_pdf(
        invoice=invoice,
        items=items_data,
        business_snapshot=business_snapshot,
        client_snapshot=client_snapshot,
        template_env=templates.env,
    )

    db.commit()

    return RedirectResponse(url=f"/invoices/{invoice.id}", status_code=303)


@router.get("/invoices/{invoice_id}")
def invoice_detail(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    items = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice_id)
        .order_by(InvoiceItem.position)
        .all()
    )
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    return templates.TemplateResponse(
        "invoice_detail.html",
        {"request": request, "invoice": invoice, "items": items, "client": client},
    )


@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice or not invoice.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    full_path = pathlib.Path(DATA_DIR) / invoice.pdf_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    return FileResponse(str(full_path), media_type="application/pdf", filename=f"{invoice.number}.pdf")


@router.post("/invoices/{invoice_id}/mark-paid")
async def invoice_mark_paid(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    paid_at_str = form.get("paid_at")
    payment_method = form.get("payment_method") or None

    if not paid_at_str:
        raise HTTPException(status_code=400, detail="paid_at is required")

    paid_at = datetime.date.fromisoformat(paid_at_str)

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    receipt_number = next_receipt_number(db, paid_at)
    invoice.paid_at = paid_at
    invoice.receipt_number = receipt_number
    invoice.payment_method = payment_method

    client_snapshot = json.loads(invoice.client_snapshot_json) if invoice.client_snapshot_json else {}
    business_snapshot = json.loads(invoice.business_snapshot_json) if invoice.business_snapshot_json else {}

    render_receipt_pdf(
        invoice=invoice,
        business_snapshot=business_snapshot,
        client_snapshot=client_snapshot,
        template_env=templates.env,
    )

    db.commit()

    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)


@router.post("/invoices/{invoice_id}/mark-unpaid")
def invoice_mark_unpaid(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Delete receipt PDF from disk if it exists
    if invoice.receipt_pdf_path:
        full_path = pathlib.Path(DATA_DIR) / invoice.receipt_pdf_path
        if full_path.exists():
            full_path.unlink()

    invoice.paid_at = None
    invoice.receipt_number = None
    invoice.receipt_pdf_path = None
    invoice.payment_method = None

    db.commit()

    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)


@router.get("/invoices/{invoice_id}/receipt.pdf")
def invoice_receipt_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice or not invoice.paid_at or not invoice.receipt_pdf_path:
        raise HTTPException(status_code=404, detail="Receipt not found")
    full_path = pathlib.Path(DATA_DIR) / invoice.receipt_pdf_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Receipt PDF file not found on disk")
    return FileResponse(str(full_path), media_type="application/pdf", filename=f"{invoice.receipt_number}.pdf")
