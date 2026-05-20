from __future__ import annotations
import datetime
from typing import Optional, List
from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None
    logo_path: Optional[str] = None
    default_payment_terms: Optional[str] = None
    default_due_days: Optional[int] = None
    default_currency: Optional[str] = None
    payment_instructions: Optional[str] = None
    default_footer_notes: Optional[str] = None


class ClientCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


class ServicePresetCreate(BaseModel):
    description: str
    unit_price: float


class ServicePresetUpdate(BaseModel):
    description: Optional[str] = None
    unit_price: Optional[float] = None


class InvoiceItemIn(BaseModel):
    description: str
    quantity: float
    unit_price: float


class InvoiceCreate(BaseModel):
    client_id: int
    issue_date: datetime.date
    due_date: datetime.date
    currency: str = "USD"
    notes: Optional[str] = None
    payment_instructions: Optional[str] = None
    items: List[InvoiceItemIn]


class MarkPaidForm(BaseModel):
    paid_at: datetime.date
    payment_method: Optional[str] = None
