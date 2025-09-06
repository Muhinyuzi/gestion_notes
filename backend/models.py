from sqlalchemy import *
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)  # ⚠️ stocker hashé
    equipe = Column(String(100))

    # Relations
    notes = relationship("Note", back_populates="auteur_obj")
    commentaires = relationship("Commentaire", back_populates="auteur_obj")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255))
    contenu = Column(Text)
    equipe = Column(String(100))
    date = Column(DateTime, default=datetime.utcnow)

    auteur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    auteur_obj = relationship("Utilisateur", back_populates="notes")

    commentaires = relationship("Commentaire", back_populates="note")


class Commentaire(Base):
    __tablename__ = "commentaires"

    id = Column(Integer, primary_key=True, index=True)
    contenu = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

    auteur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    auteur_obj = relationship("Utilisateur", back_populates="commentaires")

    note_id = Column(Integer, ForeignKey("notes.id"))
    note = relationship("Note", back_populates="commentaires")