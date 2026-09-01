from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field
from typing import Optional


def generate_uuid() -> str:
    return str(uuid4())


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)

    code_reference: str
    name: str
    description: Optional[str] = None
    price: float
    unit_measure_code: str = Field(default="94")  # Unidad DIAN
    standard_code: str = Field(default="999")  # Estándar DIAN
    tax_rate: float = Field(default=19.0)
    tax_code: str = Field(default="01")  # IVA

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
