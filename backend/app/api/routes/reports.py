from fastapi import APIRouter, Depends, Query, HTTPException, status as http_status
from sqlalchemy import func as sa_func
from sqlmodel import Session, select, func
from typing import Optional, Literal
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


VALID_STATUSES = {"draft", "pending", "validated", "rejected", "all"}


@router.get("/monthly-sales")
def monthly_sales(
    status: str = Query(default="validated", description="Filter by invoice status: draft, pending, validated, rejected, or all"),
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Return total sales and taxes grouped by month for the authenticated user.
    The `status` query parameter accepts draft, pending, validated, rejected, or all.
    """
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status filter. Allowed values: {', '.join(sorted(VALID_STATUSES))}",
        )

    month_expr = sa_func.date_trunc("month", Invoice.created_at).label("month")
    statement = (
        select(
            month_expr,
            sa_func.coalesce(sa_func.sum(Invoice.total_amount), 0).label("total_sales"),
            sa_func.coalesce(sa_func.sum(Invoice.total_tax), 0).label("total_tax"),
            sa_func.count(Invoice.id).label("invoice_count"),
        )
        .where(Invoice.user_id == current_user["id"])
        .group_by(month_expr)
        .order_by(month_expr)
    )

    if status != "all":
        statement = statement.where(Invoice.status == status)

    results = db.exec(statement).all()

    labels = []
    sales = []
    taxes = []
    counts = []
    for row in results:
        month_dt = row.month
        # date_trunc returns a datetime; format as YYYY-MM
        labels.append(month_dt.strftime("%Y-%m"))
        sales.append(float(row.total_sales))
        taxes.append(float(row.total_tax))
        counts.append(int(row.invoice_count))

    return {
        "labels": labels,
        "sales": sales,
        "taxes": taxes,
        "invoice_count": counts,
        "currency": "COP",
        "status_filter": status,
    }


@router.get("/sales-by-status")
def sales_by_status(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Return the count of invoices grouped by status for the authenticated user.
    """
    statement = (
        select(
            Invoice.status,
            sa_func.count(Invoice.id).label("count"),
        )
        .where(Invoice.user_id == current_user["id"])
        .group_by(Invoice.status)
    )

    results = db.exec(statement).all()

    # Ensure all known statuses appear in the response, even with zero count.
    counts = {status: 0 for status in ("draft", "pending", "validated", "rejected")}
    for row in results:
        if row.status in counts:
            counts[row.status] = int(row.count)

    return counts
