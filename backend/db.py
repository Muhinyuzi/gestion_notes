import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

load_dotenv()

#SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://Claude:Test1234@localhost:5432/notesdb?client_encoding=utf8"
password = quote_plus(os.getenv('DB_PASSWORD'))
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
#'postgresql://' + POSTGRES_USER + ':' + POSTGRES_PASSWORD + '@localhost:5432/' + POSTGRES_DB

# Moteur de connexion
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()