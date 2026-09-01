from app.services.factus_service import FactusMockService


def test_authenticate():
    service = FactusMockService()
    auth = service.authenticate("client_id", "client_secret")
    assert auth["token_type"] == "Bearer"
    assert "access_token" in auth
    assert auth["expires_in"] == 3600


def test_validate_invoice():
    service = FactusMockService()
    token = service.authenticate("", "")["access_token"]
    response = service.validate_invoice(token, {"reference_code": "INV-001"})
    data = response["data"]
    assert data["status"] == "validated"
    assert data["reference_code"] == "INV-001"
    assert "number" in data
    assert "cufe" in data
    assert "pdf_url" in data
    assert "xml_url" in data
