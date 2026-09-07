from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    product_id: str
    quantity: float
    discount_rate: float = 0.0


class InvoiceItemResponse(BaseModel):
    id: str
    invoice_id: str
    product_id: str
    code_reference: str
    name: str
    quantity: float
    price: float
    unit_measure_code: str
    standard_code: str
    discount_rate: float
    tax_rate: float
    tax_code: str
    subtotal: float
    tax_amount: float
    total: float

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    client_id: str
    reference_code: str
    document: str = "01"
    numbering_range_id: int = 389
    operation_type: str = "10"
    observation: Optional[str] = None
    items: List[InvoiceItemCreate]


class InvoiceResponse(BaseModel):
    id: str
    user_id: str
    client_id: str
    reference_code: str
    document: str
    numbering_range_id: int
    operation_type: str
    observation: Optional[str] = None
    status: str
    factus_number: Optional[str] = None
    cufe: Optional[str] = None
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None
    total_subtotal: float
    total_tax: float
    total_discount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


class InvoiceEmitResponse(BaseModel):
    invoice: InvoiceResponse
    factus_status: str
    message: str
