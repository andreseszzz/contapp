import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import engine
from app.models.user import User
from sqlmodel import Session, select
from supabase import create_client, Client

security = HTTPBearer()


def get_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def _get_or_create_internal_user(supabase_uid: str, email: str, full_name: str | None) -> User:
    with Session(engine) as db:
        statement = select(User).where(User.supabase_uid == supabase_uid)
        user = db.exec(statement).first()
        if not user:
            user = User(supabase_uid=supabase_uid, email=email, full_name=full_name)
            db.add(user)
            db.commit()
            db.refresh(user)
        elif full_name and not user.full_name:
            user.full_name = full_name
            db.add(user)
            db.commit()
            db.refresh(user)
        return user


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        supabase_uid = payload.get("sub")
        email = payload.get("email")
        # user_metadata is where Supabase Auth stores custom signup data such as full_name
        user_metadata = payload.get("user_metadata", {}) or {}
        full_name = user_metadata.get("full_name")
        if not supabase_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta sub",
            )
        # Map the Supabase Auth uid to our internal users.id so all routes filter consistently
        user = _get_or_create_internal_user(supabase_uid, email, full_name)
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "supabase_uid": user.supabase_uid,
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
