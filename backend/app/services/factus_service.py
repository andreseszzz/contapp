from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings


class FactusAuthError(Exception):
    pass


class FactusAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class FactusService:
    def __init__(self):
        self.base_url = settings.factus_base_url.rstrip("/")
        self.username = settings.factus_username
        self.password = settings.factus_password
        self.client_id = settings.factus_client_id
        self.client_secret = settings.factus_client_secret
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: Optional[datetime] = None

    def _is_token_valid(self) -> bool:
        if not self.access_token or not self.expires_at:
            return False
        # Renovar 60 segundos antes de expirar
        return datetime.utcnow() < (self.expires_at - timedelta(seconds=60))

    def _set_token(self, token_data: Dict[str, Any]) -> None:
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 600)
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    def authenticate(self) -> Dict[str, Any]:
        url = f"{self.base_url}/oauth/token"
        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }
        try:
            response = httpx.post(url, data=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            self._set_token(data)
            return data
        except httpx.HTTPStatusError as exc:
            raise FactusAuthError(
                f"Factus authentication failed: {exc.response.status_code} - {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise FactusAuthError(f"Factus authentication request failed: {str(exc)}")

    def _refresh_token(self) -> Dict[str, Any]:
        if not self.refresh_token:
            return self.authenticate()

        url = f"{self.base_url}/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }
        try:
            response = httpx.post(url, data=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            self._set_token(data)
            return data
        except httpx.HTTPStatusError:
            # Si el refresh falla, reautenticamos con usuario/contraseña
            return self.authenticate()
        except httpx.RequestError:
            return self.authenticate()

    def _ensure_token(self) -> str:
        if not self._is_token_valid():
            if self.refresh_token:
                self._refresh_token()
            else:
                self.authenticate()
        return self.access_token

    def _request(
        self,
        method: str,
        path: str,
        json_data: Any = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        token = self._ensure_token()
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            # Si expiró el token, intentar refrescar una vez y reintentar
            if exc.response.status_code == 401:
                self._refresh_token()
                token = self.access_token
                headers["Authorization"] = f"Bearer {token}"
                try:
                    response = httpx.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_data,
                        params=params,
                        timeout=60.0,
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as exc2:
                    raise FactusAPIError(
                        f"Factus API error after retry: {exc2.response.status_code}",
                        status_code=exc2.response.status_code,
                        response_body=exc2.response.text,
                    )
            body = exc.response.text
            raise FactusAPIError(
                f"Factus API error: {exc.response.status_code}",
                status_code=exc.response.status_code,
                response_body=body,
            )
        except httpx.RequestError as exc:
            raise FactusAPIError(f"Factus API request failed: {str(exc)}")

    def validate_invoice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self._request("POST", "/v2/bills/validate", json_data=payload)
        except FactusAPIError as exc:
            if exc.status_code == 409:
                self.delete_pending_invoice(payload["reference_code"])
                return self._request("POST", "/v2/bills/validate", json_data=payload)
            raise

    def get_invoice(self, number: str) -> Dict[str, Any]:
        return self._request("GET", f"/v2/bills/{number}")

    def delete_pending_invoice(self, reference_code: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/v2/bills/destroy/reference/{reference_code}")

    def download_pdf(self, number: str) -> bytes:
        token = self._ensure_token()
        url = f"{self.base_url}/v2/bills/{number}/pdf"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/pdf"}
        response = httpx.get(url, headers=headers, timeout=60.0)
        response.raise_for_status()
        return response.content

    def download_xml(self, number: str) -> bytes:
        token = self._ensure_token()
        url = f"{self.base_url}/v2/bills/{number}/xml"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/xml"}
        response = httpx.get(url, headers=headers, timeout=60.0)
        response.raise_for_status()
        return response.content

    def get_numbering_ranges(self) -> List[Dict[str, Any]]:
        result = self._request("GET", "/v2/numbering-ranges")
        return result.get("data", {}).get("ranges", []) if isinstance(result, dict) else []


def get_factus_service() -> FactusService:
    return FactusService()
