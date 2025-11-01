# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# -----------------------------------------------------------
# 🔹 Moteur de base de données (depuis config.py)
# -----------------------------------------------------------
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL non définie dans le fichier .env ou dans config.py.\n"
        "Exemple attendu : postgresql+psycopg2://user:password@localhost:5432/notesdb"
    )

# Crée le moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # utile en dev, silencieux en prod
    future=True,
)

# Crée une session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ORM
Base = declarative_base()


# -----------------------------------------------------------
# 🔹 Dépendance FastAPI pour obtenir une session DB
# -----------------------------------------------------------
def get_db():
    """
    Fournit une session SQLAlchemy à chaque requête.
    Ferme automatiquement la session à la fin.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
