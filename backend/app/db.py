# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

Base = declarative_base()

# ✅ TEST MODE: use engine provided by tests
if os.getenv("TESTING") == "1":
    from app.tests.conftest import engine as test_engine
    engine = test_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # ✅ Normal mode: load real DB from config
    DATABASE_URL = settings.DATABASE_URL
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL manquant")

    engine = create_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
