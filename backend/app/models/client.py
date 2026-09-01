from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field
from typing import Optional


def generate_uuid() -> str:
    return str(uuid4())


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)

    identification_document_code: str = Field(default="31")  # Código DIAN
    identification: str = Field(index=True)
    company: Optional[str] = None
    trade_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    legal_organization_code: str = Field(default="1")
    tribute_code: str = Field(default="ZZ")
    municipality_code: str = Field(default="11001")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
