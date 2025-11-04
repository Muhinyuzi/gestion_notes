from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime


# ---------------- NOTES ----------------
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False, index=True)
    contenu = Column(Text, nullable=False)
    equipe = Column(String(100), index=True)

    auteur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="CASCADE"), index=True)

        # 🆕 Nouveaux champs
    categorie = Column(String, nullable=True)
    priorite = Column(String, default="Moyenne")
    likes = Column(Integer, default=0)
    nb_vues = Column(Integer, default=0)
    resume_ia = Column(Text, nullable=True)

    auteur = relationship("Utilisateur", back_populates="notes")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=None, onupdate=func.now(), index=True)

    # Relations
    commentaires = relationship("Commentaire", back_populates="note", cascade="all, delete-orphan")
    fichiers = relationship("FichierNote", back_populates="note", cascade="all, delete-orphan")  # 🔹 fichiers multiples
    eleves = relationship("Eleve", back_populates="note") 



# 🔹 Index supplémentaires pour optimiser les requêtes fréquentes
Index("idx_note_auteur", Note.auteur_id)
Index("idx_note_equipe", Note.equipe)