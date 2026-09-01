from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    code_reference: str
    name: str
    description: Optional[str] = None
    price: float
    unit_measure_code: str = "94"
    standard_code: str = "999"
    tax_rate: float = 19.0
    tax_code: str = "01"


class ProductUpdate(BaseModel):
    code_reference: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    unit_measure_code: Optional[str] = None
    standard_code: Optional[str] = None
    tax_rate: Optional[float] = None
    tax_code: Optional[str] = None


class ProductResponse(ProductCreate):
    id: str
    user_id: str

    class Config:
        from_attributes = True
