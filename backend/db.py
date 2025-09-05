from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chaîne de connexion PostgreSQL (à adapter à ton environnement)
# Format : postgresql://user:password@host:port/database
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/notesdb"

# Moteur de connexion
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session = objet pour exécuter les requêtes SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = classe mère pour définir les modèles
Base = declarative_base()

# Dépendance pour obtenir une session DB (FastAPI l’utilise avec Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()