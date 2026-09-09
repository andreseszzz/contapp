import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import engine
from app.models.user import User
from sqlmodel import Session, select
from supabase import create_client, Client

security = HTTPBearer()

# Cache the JWKS client so keys are fetched once and refreshed as needed.
_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.supabase_jwks_url)
    return _jwks_client


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
        # Verify the token signature against Supabase Auth JWKS and standard claims.
        # This blocks forged/self-signed tokens and prevents a malicious actor from
        # choosing an arbitrary `sub` to impersonate another user.
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=settings.supabase_jwt_issuer,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

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
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta email",
        )

    # Map the Supabase Auth uid to our internal users.id so all routes filter consistently
    user = _get_or_create_internal_user(supabase_uid, email, full_name)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "supabase_uid": user.supabase_uid,
    }
