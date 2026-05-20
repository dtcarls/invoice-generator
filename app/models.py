from sqlalchemy import (
    Column, Integer, Text, Numeric, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.db import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    business_name = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(Text)
    region = Column(Text)
    postal_code = Column(Text)
    country = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    website = Column(Text)
    tax_id = Column(Text)
    logo_path = Column(Text)
    default_payment_terms = Column(Text)
    default_due_days = Column(Integer)
    default_currency = Column(Text)
    payment_instructions = Column(Text)
    default_footer_notes = Column(Text)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    contact_name = Column(Text)
    email = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(Text)
    region = Column(Text)
    postal_code = Column(Text)
    country = Column(Text)
    notes = Column(Text)
    archived = Column(Integer, default=0)


class ServicePreset(Base):
    __tablename__ = "service_presets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    archived = Column(Integer, default=0)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Text, unique=True, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", foreign_keys=[client_id], lazy="select")
    client_snapshot_json = Column(Text)
    business_snapshot_json = Column(Text)
    currency = Column(Text, nullable=False, default="USD")
    notes = Column(Text)
    payment_instructions = Column(Text)
    total = Column(Numeric, nullable=False, default=0)
    pdf_path = Column(Text)
    paid_at = Column(Date)
    receipt_number = Column(Text, unique=True)
    receipt_pdf_path = Column(Text)
    payment_method = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    line_total = Column(Numeric, nullable=False)
