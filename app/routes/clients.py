from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Client
from app.templates_config import templates

router = APIRouter()


@router.get("/clients")
def clients_list(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Client).filter(Client.archived == 0).all()
    return templates.TemplateResponse(
        "clients_list.html",
        {"request": request, "clients": clients},
    )


@router.get("/clients/new")
def client_new(request: Request):
    return templates.TemplateResponse(
        "client_form.html",
        {"request": request, "client": None, "action_url": "/clients"},
    )


@router.post("/clients")
async def client_create(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    client = Client(
        name=form.get("name", "").strip(),
        contact_name=form.get("contact_name") or None,
        email=form.get("email") or None,
        address_line1=form.get("address_line1") or None,
        address_line2=form.get("address_line2") or None,
        city=form.get("city") or None,
        region=form.get("region") or None,
        postal_code=form.get("postal_code") or None,
        country=form.get("country") or None,
        notes=form.get("notes") or None,
    )
    db.add(client)
    db.commit()
    return RedirectResponse(url="/clients", status_code=303)


@router.get("/clients/{client_id}/edit")
def client_edit(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return templates.TemplateResponse(
        "client_form.html",
        {"request": request, "client": client, "action_url": f"/clients/{client_id}"},
    )


@router.post("/clients/{client_id}")
async def client_update(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    form = await request.form()
    client.name = form.get("name", client.name).strip()
    client.contact_name = form.get("contact_name") or None
    client.email = form.get("email") or None
    client.address_line1 = form.get("address_line1") or None
    client.address_line2 = form.get("address_line2") or None
    client.city = form.get("city") or None
    client.region = form.get("region") or None
    client.postal_code = form.get("postal_code") or None
    client.country = form.get("country") or None
    client.notes = form.get("notes") or None
    db.commit()
    return RedirectResponse(url="/clients", status_code=303)


@router.post("/clients/{client_id}/archive")
def client_archive(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.archived = 1
    db.commit()
    return RedirectResponse(url="/clients", status_code=303)
