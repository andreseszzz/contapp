from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


def generate_uuid() -> str:
    return str(uuid4())


class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    client_id: str = Field(foreign_key="clients.id", index=True)

    reference_code: str = Field(index=True)
    document: str = Field(default="01")  # Factura de venta
    numbering_range_id: int = Field(default=1)
    operation_type: str = Field(default="10")
    observation: Optional[str] = None

    status: str = Field(default="draft")  # draft, pending, validated, rejected
    factus_number: Optional[str] = None
    cufe: Optional[str] = None
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None
    factus_response: Optional[str] = None

    total_subtotal: float = Field(default=0.0)
    total_tax: float = Field(default=0.0)
    total_discount: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    items: List["InvoiceItem"] = Relationship(back_populates="invoice")


class InvoiceItem(SQLModel, table=True):
    __tablename__ = "invoice_items"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    invoice_id: str = Field(foreign_key="invoices.id", index=True)
    product_id: str = Field(foreign_key="products.id", index=True)

    code_reference: str
    name: str
    quantity: float
    price: float
    unit_measure_code: str
    standard_code: str
    discount_rate: float = Field(default=0.0)
    tax_rate: float = Field(default=19.0)
    tax_code: str = Field(default="01")
    subtotal: float
    tax_amount: float
    total: float

    invoice: Optional[Invoice] = Relationship(back_populates="items")
