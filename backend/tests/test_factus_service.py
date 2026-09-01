from unittest.mock import patch
import httpx
from app.services.factus_service import FactusService, get_factus_service, FactusAPIError


def _build_request(method="GET", url="https://api-sandbox.factus.com.co/test"):
    return httpx.Request(method=method, url=url)


def _json_response(status_code=200, json_data=None, request=None):
    return httpx.Response(
        status_code=status_code,
        json=json_data or {},
        request=request or _build_request(),
    )


def test_authenticate_success():
    service = FactusService()
    request = httpx.Request("POST", "https://api-sandbox.factus.com.co/oauth/token")
    response = _json_response(
        200,
        {
            "token_type": "Bearer",
            "expires_in": 3600,
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        },
        request=request,
    )

    with patch("httpx.post", return_value=response) as mock_post:
        data = service.authenticate()

    assert data["access_token"] == "test-access-token"
    assert data["refresh_token"] == "test-refresh-token"
    assert service.access_token == "test-access-token"
    mock_post.assert_called_once()


def test_validate_invoice_success():
    service = FactusService()
    service.access_token = "test-access-token"
    service.expires_at = __import__("datetime").datetime.utcnow() + __import__("datetime").timedelta(hours=1)

    request = httpx.Request("POST", "https://api-sandbox.factus.com.co/v2/bills/validate")
    response = _json_response(
        200,
        {
            "status": "Created",
            "message": "Documento registrado y validado con éxito",
            "data": {
                "number": "SETP990000001",
                "cufe": "abc123",
                "is_validated": True,
                "links": {
                    "public_url": "https://example.com/pdf",
                },
            },
        },
        request=request,
    )

    with patch("httpx.request", return_value=response):
        result = service.validate_invoice({"reference_code": "INV-001"})

    assert result["data"]["number"] == "SETP990000001"
    assert result["data"]["cufe"] == "abc123"


def test_validate_invoice_409_then_retry():
    service = FactusService()
    service.access_token = "test-access-token"
    service.expires_at = __import__("datetime").datetime.utcnow() + __import__("datetime").timedelta(hours=1)

    conflict_request = httpx.Request("POST", "https://api-sandbox.factus.com.co/v2/bills/validate")
    conflict_response = httpx.Response(
        status_code=409,
        json={"status": "Conflict", "message": "Se encontró una factura pendiente por enviar a la DIAN"},
        request=conflict_request,
    )

    success_request = httpx.Request("POST", "https://api-sandbox.factus.com.co/v2/bills/validate")
    success_response = _json_response(
        200,
        {
            "status": "Created",
            "message": "Documento registrado y validado con éxito",
            "data": {
                "number": "SETP990000002",
                "cufe": "def456",
                "is_validated": True,
            },
        },
        request=success_request,
    )

    delete_response = _json_response(200, {"status": "Deleted"})
    refresh_request = httpx.Request("POST", "https://api-sandbox.factus.com.co/oauth/token")
    refresh_response = _json_response(
        200,
        {
            "access_token": "refreshed-token",
            "refresh_token": "refresh-token",
            "expires_in": 3600,
        },
        request=refresh_request,
    )

    with patch("httpx.request", side_effect=[conflict_response, success_response]) as mock_request:
        with patch("httpx.post", return_value=refresh_response):
            with patch.object(service, "delete_pending_invoice", return_value=delete_response):
                result = service.validate_invoice({"reference_code": "INV-002"})

    assert result["data"]["number"] == "SETP990000002"
    assert mock_request.call_count == 2


def test_validate_invoice_error():
    service = FactusService()
    service.access_token = "test-access-token"
    service.expires_at = __import__("datetime").datetime.utcnow() + __import__("datetime").timedelta(hours=1)

    request = httpx.Request("POST", "https://api-sandbox.factus.com.co/v2/bills/validate")
    response = httpx.Response(
        status_code=400,
        json={"status": "Bad Request", "message": "Invalid payload"},
        request=request,
    )

    with patch("httpx.request", return_value=response):
        try:
            service.validate_invoice({"reference_code": "INV-003"})
            assert False, "Expected FactusAPIError"
        except FactusAPIError as exc:
            assert exc.status_code == 400


def test_get_factus_service_returns_instance():
    s1 = get_factus_service()
    s2 = get_factus_service()
    assert isinstance(s1, FactusService)
    assert isinstance(s2, FactusService)
