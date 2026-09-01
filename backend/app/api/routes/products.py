from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


@router.post("/", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    product = Product(**data.model_dump(), user_id=current_user["id"])
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductResponse])
def list_products(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Product).where(Product.user_id == current_user["id"])
    return db.exec(statement).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Product).where(
        Product.id == product_id, Product.user_id == current_user["id"]
    )
    product = db.exec(statement).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Product).where(
        Product.id == product_id, Product.user_id == current_user["id"]
    )
    product = db.exec(statement).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Product).where(
        Product.id == product_id, Product.user_id == current_user["id"]
    )
    product = db.exec(statement).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    db.delete(product)
    db.commit()
    return None
