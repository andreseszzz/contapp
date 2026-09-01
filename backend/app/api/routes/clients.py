from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.post("/", response_model=ClientResponse)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    client = Client(**data.model_dump(), user_id=current_user["id"])
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Client).where(Client.user_id == current_user["id"])
    return db.exec(statement).all()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Client).where(
        Client.id == client_id, Client.user_id == current_user["id"]
    )
    client = db.exec(statement).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    data: ClientUpdate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Client).where(
        Client.id == client_id, Client.user_id == current_user["id"]
    )
    client = db.exec(statement).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(client, key, value)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Client).where(
        Client.id == client_id, Client.user_id == current_user["id"]
    )
    client = db.exec(statement).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    db.delete(client)
    db.commit()
    return None
