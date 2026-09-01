from pydantic import BaseModel
from typing import Optional


class ClientCreate(BaseModel):
    identification_document_code: str = "31"
    identification: str
    company: Optional[str] = None
    trade_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    legal_organization_code: str = "1"
    tribute_code: str = "ZZ"
    municipality_code: str = "11001"


class ClientUpdate(BaseModel):
    identification_document_code: Optional[str] = None
    identification: Optional[str] = None
    company: Optional[str] = None
    trade_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    legal_organization_code: Optional[str] = None
    tribute_code: Optional[str] = None
    municipality_code: Optional[str] = None


class ClientResponse(ClientCreate):
    id: str
    user_id: str

    class Config:
        from_attributes = True
