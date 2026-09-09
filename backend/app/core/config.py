import os
from pydantic_settings import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ENV_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    app_name: str = "Contapp"
    debug: bool = True
    secret_key: str = "change-me"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_issuer: str | None = None
    # JWKS endpoint used to verify Supabase Auth access tokens (EC256).
    # Defaults to {supabase_url}/auth/v1/.well-known/jwks.json
    supabase_jwks_url: str | None = None

    database_url: str

    factus_base_url: str = "https://api-sandbox.factus.com.co"
    factus_username: str = ""
    factus_password: str = ""
    factus_client_id: str = ""
    factus_client_secret: str = ""

    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Post-process defaults that depend on other settings.
if settings.supabase_jwt_issuer is None:
    settings.supabase_jwt_issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
if settings.supabase_jwks_url is None:
    settings.supabase_jwks_url = f"{settings.supabase_jwt_issuer}/.well-known/jwks.json"
