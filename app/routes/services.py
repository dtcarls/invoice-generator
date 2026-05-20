from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ServicePreset
from app.templates_config import templates

router = APIRouter()


@router.get("/services")
def services_list(request: Request, db: Session = Depends(get_db)):
    presets = db.query(ServicePreset).filter(ServicePreset.archived == 0).all()
    return templates.TemplateResponse(
        "services_list.html",
        {"request": request, "presets": presets},
    )


@router.get("/services/new")
def service_new(request: Request):
    return templates.TemplateResponse(
        "service_form.html",
        {"request": request, "preset": None},
    )


@router.post("/services")
async def service_create(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    preset = ServicePreset(
        description=form.get("description", "").strip(),
        unit_price=float(form.get("unit_price", 0)),
    )
    db.add(preset)
    db.commit()
    return RedirectResponse(url="/services", status_code=303)


@router.get("/services/{preset_id}/edit")
def service_edit(preset_id: int, request: Request, db: Session = Depends(get_db)):
    preset = db.query(ServicePreset).filter(ServicePreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Service preset not found")
    return templates.TemplateResponse(
        "service_form.html",
        {"request": request, "preset": preset},
    )


@router.post("/services/{preset_id}")
async def service_update(preset_id: int, request: Request, db: Session = Depends(get_db)):
    preset = db.query(ServicePreset).filter(ServicePreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Service preset not found")
    form = await request.form()
    preset.description = form.get("description", preset.description).strip()
    preset.unit_price = float(form.get("unit_price", preset.unit_price))
    db.commit()
    return RedirectResponse(url="/services", status_code=303)


@router.post("/services/{preset_id}/archive")
def service_archive(preset_id: int, db: Session = Depends(get_db)):
    preset = db.query(ServicePreset).filter(ServicePreset.id == preset_id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Service preset not found")
    preset.archived = 1
    db.commit()
    return RedirectResponse(url="/services", status_code=303)
