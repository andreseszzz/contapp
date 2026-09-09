"""Integration tests for the reports endpoints using the real Supabase database.

These tests run against the configured DATABASE_URL (Supabase) and verify that
reports are isolated per user and that the new monthly-sales/status endpoints
behave correctly.
"""
import os
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.main import app
from app.core.database import engine, get_session
from app.core.security import get_current_user
from app.models.user import User
from app.models.client import Client
from app.models.product import Product
from app.models.invoice import Invoice, InvoiceItem


TEST_USER_A = {
    "id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1",
    "email": "test.user.a@contapp.example",
    "full_name": "Test User A",
    "supabase_uid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
}

TEST_USER_B = {
    "id": "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2",
    "email": "test.user.b@contapp.example",
    "full_name": "Test User B",
    "supabase_uid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
}


def override_get_current_user(user):
    def _override():
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "supabase_uid": user["supabase_uid"],
        }
    return _override


def _ensure_user(user_payload):
    with Session(engine) as db:
        user = db.exec(select(User).where(User.id == user_payload["id"])).first()
        if not user:
            user = User(
                id=user_payload["id"],
                email=user_payload["email"],
                full_name=user_payload["full_name"],
                supabase_uid=user_payload["supabase_uid"],
            )
            db.add(user)
            db.commit()
        return user


def _create_invoice(db, user_id, status, total_amount, total_tax, month_offset=0):
    client_id = str(uuid.uuid4())
    client = Client(
        id=client_id,
        user_id=user_id,
        identification="123456",
        identification_document_code="31",
        legal_organization_code="1",
        tribute_code="ZZ",
        municipality_code="11001",
        created_at=datetime.utcnow() - timedelta(days=month_offset * 30),
        updated_at=datetime.utcnow() - timedelta(days=month_offset * 30),
    )
    db.add(client)

    product_id = str(uuid.uuid4())
    product = Product(
        id=product_id,
        user_id=user_id,
        code_reference="TEST01",
        name="Test item",
        price=total_amount - total_tax,
        unit_measure_code="94",
        standard_code="999",
        tax_rate=19.0,
        tax_code="01",
        created_at=datetime.utcnow() - timedelta(days=month_offset * 30),
        updated_at=datetime.utcnow() - timedelta(days=month_offset * 30),
    )
    db.add(product)

    invoice_id = str(uuid.uuid4())
    created_at = datetime.utcnow() - timedelta(days=month_offset * 30)
    invoice = Invoice(
        id=invoice_id,
        user_id=user_id,
        client_id=client_id,
        reference_code=f"TEST-{invoice_id[:8]}",
        document="01",
        numbering_range_id=389,
        operation_type="10",
        status=status,
        total_subtotal=total_amount - total_tax,
        total_tax=total_tax,
        total_discount=0.0,
        total_amount=total_amount,
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(invoice)

    item = InvoiceItem(
        id=str(uuid.uuid4()),
        invoice_id=invoice_id,
        product_id=product_id,
        code_reference="TEST01",
        name="Test item",
        quantity=1,
        price=total_amount - total_tax,
        unit_measure_code="94",
        standard_code="999",
        discount_rate=0.0,
        tax_rate=19.0,
        tax_code="01",
        subtotal=total_amount - total_tax,
        tax_amount=total_tax,
        total=total_amount,
    )
    db.add(item)

    db.commit()
    return invoice_id


def _cleanup_user_data(db, user_id):
    from sqlalchemy import text
    db.exec(text(f"DELETE FROM public.invoice_items WHERE invoice_id IN (SELECT id FROM public.invoices WHERE user_id = '{user_id}')"))
    db.exec(text(f"DELETE FROM public.invoices WHERE user_id = '{user_id}'"))
    db.exec(text(f"DELETE FROM public.clients WHERE user_id = '{user_id}'"))
    db.exec(text(f"DELETE FROM public.products WHERE user_id = '{user_id}'"))
    db.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # Ensure both test users exist before running tests.
    _ensure_user(TEST_USER_A)
    _ensure_user(TEST_USER_B)


@pytest.fixture
def clean_user_a_invoices():
    with Session(engine) as db:
        _cleanup_user_data(db, TEST_USER_A["id"])
    yield
    with Session(engine) as db:
        _cleanup_user_data(db, TEST_USER_A["id"])


@pytest.fixture
def clean_user_b_invoices():
    with Session(engine) as db:
        _cleanup_user_data(db, TEST_USER_B["id"])
    yield
    with Session(engine) as db:
        _cleanup_user_data(db, TEST_USER_B["id"])


def _build_test_app(user_payload):
    """Build a fresh FastAPI app with isolated dependency overrides for a test user.

    Using a per-client app copy avoids shared mutable ``app.dependency_overrides``
    leaking between TestClient instances, which was causing user-isolation tests
    to bind the wrong user in FastAPI 0.115.0.
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.api.routes import auth, clients, products, invoices, reports

    test_app = FastAPI(title=app.title)
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    test_app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
    test_app.include_router(products.router, prefix="/api/products", tags=["products"])
    test_app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
    test_app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    test_app.dependency_overrides[get_session] = lambda: next(get_session())
    test_app.dependency_overrides[get_current_user] = override_get_current_user(user_payload)
    return test_app


@pytest.fixture
def client_a():
    test_app = _build_test_app(TEST_USER_A)
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def client_b():
    test_app = _build_test_app(TEST_USER_B)
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def clean_invoices(clean_user_a_invoices, clean_user_b_invoices):
    # Composite fixture that cleans invoices for both test users.
    yield


def test_monthly_sales_requires_auth():
    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.pop(get_current_user, None)
    try:
        with TestClient(app) as client:
            response = client.get("/api/reports/monthly-sales")
        assert response.status_code == 403
    finally:
        app.dependency_overrides = original_overrides


def test_sales_by_status_requires_auth():
    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.pop(get_current_user, None)
    try:
        with TestClient(app) as client:
            response = client.get("/api/reports/sales-by-status")
        assert response.status_code == 403
    finally:
        app.dependency_overrides = original_overrides


def test_monthly_sales_status_filter(clean_invoices, client_a):
    with Session(engine) as db:
        _create_invoice(db, TEST_USER_A["id"], "validated", 1190.0, 190.0, month_offset=1)
        _create_invoice(db, TEST_USER_A["id"], "draft", 500.0, 0.0, month_offset=1)
        _create_invoice(db, TEST_USER_A["id"], "validated", 2380.0, 380.0, month_offset=0)

    # Default filter is validated.
    response = client_a.get("/api/reports/monthly-sales")
    assert response.status_code == 200
    data = response.json()
    assert data["status_filter"] == "validated"
    assert sum(data["sales"]) == 1190.0 + 2380.0
    assert sum(data["taxes"]) == 190.0 + 380.0

    # Filter by draft.
    response = client_a.get("/api/reports/monthly-sales?status=draft")
    assert response.status_code == 200
    data = response.json()
    assert data["status_filter"] == "draft"
    assert sum(data["sales"]) == 500.0

    # All statuses.
    response = client_a.get("/api/reports/monthly-sales?status=all")
    assert response.status_code == 200
    data = response.json()
    assert data["status_filter"] == "all"
    assert sum(data["sales"]) == 1190.0 + 500.0 + 2380.0


def test_monthly_sales_invalid_status(client_a):
    response = client_a.get("/api/reports/monthly-sales?status=invalid")
    assert response.status_code == 422


def test_sales_by_status_is_user_isolated(clean_invoices, client_a, client_b):
    with Session(engine) as db:
        _create_invoice(db, TEST_USER_A["id"], "validated", 1190.0, 190.0, month_offset=0)
        _create_invoice(db, TEST_USER_A["id"], "draft", 500.0, 0.0, month_offset=0)
        _create_invoice(db, TEST_USER_B["id"], "validated", 2000.0, 200.0, month_offset=0)

    response = client_a.get("/api/reports/sales-by-status")
    assert response.status_code == 200
    data = response.json()
    assert data["validated"] == 1
    assert data["draft"] == 1
    assert data["pending"] == 0
    assert data["rejected"] == 0

    response = client_b.get("/api/reports/sales-by-status")
    assert response.status_code == 200
    data = response.json()
    assert data["validated"] == 1
    assert data["draft"] == 0


def test_monthly_sales_is_user_isolated(clean_invoices, client_a, client_b):
    with Session(engine) as db:
        _create_invoice(db, TEST_USER_A["id"], "validated", 1190.0, 190.0, month_offset=0)
        _create_invoice(db, TEST_USER_B["id"], "validated", 5000.0, 500.0, month_offset=0)

    response = client_a.get("/api/reports/monthly-sales?status=all")
    assert response.status_code == 200
    data = response.json()
    assert sum(data["sales"]) == 1190.0

    response = client_b.get("/api/reports/monthly-sales?status=all")
    assert response.status_code == 200
    data = response.json()
    assert sum(data["sales"]) == 5000.0
