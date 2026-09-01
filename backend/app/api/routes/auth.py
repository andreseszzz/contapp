from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter()


@router.post("/profile", response_model=UserResponse)
def create_or_update_profile(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(User).where(User.supabase_uid == current_user["id"])
    user = db.exec(statement).first()
    if not user:
        user = User(
            supabase_uid=current_user["id"],
            email=current_user["email"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        supabase_uid=user.supabase_uid,
    )


@router.get("/me", response_model=UserResponse)
def me(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(User).where(User.supabase_uid == current_user["id"])
    user = db.exec(statement).first()
    if not user:
        user = User(
            supabase_uid=current_user["id"],
            email=current_user["email"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        supabase_uid=user.supabase_uid,
    )
