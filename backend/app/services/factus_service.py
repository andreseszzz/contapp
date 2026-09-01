import random
import string
from datetime import datetime
from typing import Dict, Any


class FactusMockService:
    def __init__(self, base_url: str = "https://api-sandbox.factus.com.co"):
        self.base_url = base_url

    def authenticate(self, client_id: str, client_secret: str) -> Dict[str, Any]:
        return {
            "access_token": "mock_token_" + "".join(random.choices(string.ascii_letters + string.digits, k=20)),
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def validate_invoice(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        number = f"SETT{random.randint(100000, 999999)}"
        cufe = "".join(random.choices(string.ascii_uppercase + string.digits, k=96))
        return {
            "data": {
                "number": number,
                "reference_code": payload.get("reference_code"),
                "cufe": cufe,
                "status": "validated",
                "qr": f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cufe}",
                "pdf_url": f"https://mock.factus.com.co/pdf/{number}.pdf",
                "xml_url": f"https://mock.factus.com.co/xml/{number}.xml",
                "errors": [],
            }
        }

    def get_invoice_status(self, token: str, number: str) -> Dict[str, Any]:
        return {
            "data": {
                "number": number,
                "status": "validated",
                "cufe": "".join(random.choices(string.ascii_uppercase + string.digits, k=96)),
            }
        }


def get_factus_service() -> FactusMockService:
    return FactusMockService()
