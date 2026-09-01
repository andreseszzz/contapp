from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.models.client import Client
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceEmitResponse
from app.services.factus_service import get_factus_service

router = APIRouter()


def _calculate_item_totals(item_data, product):
    quantity = item_data.quantity
    price = product.price
    discount_rate = item_data.discount_rate or 0.0
    tax_rate = product.tax_rate

    subtotal = quantity * price
    discount_amount = subtotal * (discount_rate / 100)
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * (tax_rate / 100)
    total = taxable_amount + tax_amount

    return {
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
    }


@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    client = db.get(Client, data.client_id)
    if not client or client.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    invoice = Invoice(
        user_id=current_user["id"],
        client_id=data.client_id,
        reference_code=data.reference_code,
        document=data.document,
        numbering_range_id=data.numbering_range_id,
        operation_type=data.operation_type,
        observation=data.observation,
        status="draft",
    )
    db.add(invoice)
    db.flush()

    total_subtotal = 0.0
    total_tax = 0.0
    total_discount = 0.0

    for item_data in data.items:
        product = db.get(Product, item_data.product_id)
        if not product or product.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found",
            )

        totals = _calculate_item_totals(item_data, product)
        discount_amount = (item_data.quantity * product.price) * ((item_data.discount_rate or 0.0) / 100)

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.product_id,
            code_reference=product.code_reference,
            name=product.name,
            quantity=item_data.quantity,
            price=product.price,
            unit_measure_code=product.unit_measure_code,
            standard_code=product.standard_code,
            discount_rate=item_data.discount_rate or 0.0,
            tax_rate=product.tax_rate,
            tax_code=product.tax_code,
            subtotal=totals["subtotal"],
            tax_amount=totals["tax_amount"],
            total=totals["total"],
        )
        db.add(invoice_item)

        total_subtotal += totals["subtotal"]
        total_tax += totals["tax_amount"]
        total_discount += discount_amount

    invoice.total_subtotal = round(total_subtotal, 2)
    invoice.total_tax = round(total_tax, 2)
    invoice.total_discount = round(total_discount, 2)
    invoice.total_amount = round(total_subtotal - total_discount + total_tax, 2)

    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Invoice).where(Invoice.user_id == current_user["id"])
    return db.exec(statement).all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    invoice = db.get(Invoice, invoice_id)
    if not invoice or invoice.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/emit", response_model=InvoiceEmitResponse)
def emit_invoice(
    invoice_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    invoice = db.get(Invoice, invoice_id)
    if not invoice or invoice.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    if invoice.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has already been emitted",
        )

    factus = get_factus_service()
    auth = factus.authenticate(
        settings.factus_client_id,
        settings.factus_client_secret,
    )

    client = db.get(Client, invoice.client_id)
    items = []
    for item in invoice.items:
        items.append(
            {
                "code_reference": item.code_reference,
                "name": item.name,
                "quantity": str(item.quantity),
                "discount_rate": str(item.discount_rate),
                "price": str(item.price),
                "unit_measure_code": item.unit_measure_code,
                "standard_code": item.standard_code,
                "taxes": [{"code": item.tax_code, "rate": str(item.tax_rate)}],
            }
        )

    payload = {
        "reference_code": invoice.reference_code,
        "document": invoice.document,
        "numbering_range_id": invoice.numbering_range_id,
        "operation_type": invoice.operation_type,
        "observation": invoice.observation,
        "customer": {
            "identification_document_code": client.identification_document_code,
            "identification": client.identification,
            "company": client.company,
            "trade_name": client.trade_name,
            "address": client.address,
            "email": client.email,
            "phone": client.phone,
            "legal_organization_code": client.legal_organization_code,
            "tribute_code": client.tribute_code,
            "municipality_code": client.municipality_code,
        },
        "items": items,
    }

    response = factus.validate_invoice(auth["access_token"], payload)
    data = response.get("data", {})

    invoice.status = "validated" if data.get("status") == "validated" else "rejected"
    invoice.factus_number = data.get("number")
    invoice.cufe = data.get("cufe")
    invoice.pdf_url = data.get("pdf_url")
    invoice.xml_url = data.get("xml_url")
    invoice.factus_response = str(data)

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return InvoiceEmitResponse(
        invoice=invoice,
        factus_status=invoice.status,
        message="Invoice emitted successfully (mock mode)",
    )
