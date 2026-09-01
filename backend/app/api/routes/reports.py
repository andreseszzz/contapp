from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import Optional
from datetime import date
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.invoice import Invoice

router = APIRouter()


@router.get("/sales-summary")
def sales_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Invoice).where(Invoice.user_id == current_user["id"])
    if start_date:
        statement = statement.where(Invoice.created_at >= start_date)
    if end_date:
        statement = statement.where(Invoice.created_at <= end_date)

    invoices = db.exec(statement).all()
    total_sales = sum(inv.total_amount for inv in invoices)
    total_tax = sum(inv.total_tax for inv in invoices)
    count = len(invoices)

    return {
        "total_sales": round(total_sales, 2),
        "total_tax": round(total_tax, 2),
        "invoice_count": count,
        "currency": "COP",
    }


@router.get("/taxes")
def taxes_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Invoice).where(
        Invoice.user_id == current_user["id"],
        Invoice.status == "validated",
    )
    if start_date:
        statement = statement.where(Invoice.created_at >= start_date)
    if end_date:
        statement = statement.where(Invoice.created_at <= end_date)

    invoices = db.exec(statement).all()
    total_iva = sum(inv.total_tax for inv in invoices)

    return {
        "total_iva": round(total_iva, 2),
        "invoice_count": len(invoices),
        "currency": "COP",
    }


@router.get("/accounts-receivable")
def accounts_receivable(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Invoice).where(
        Invoice.user_id == current_user["id"],
        Invoice.status == "validated",
    )
    invoices = db.exec(statement).all()
    total = sum(inv.total_amount for inv in invoices)

    return {
        "total_accounts_receivable": round(total, 2),
        "invoice_count": len(invoices),
        "currency": "COP",
    }
