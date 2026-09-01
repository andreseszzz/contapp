from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

engine = create_engine(settings.database_url.replace("postgresql://", "postgresql+psycopg://"), echo=settings.debug)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
