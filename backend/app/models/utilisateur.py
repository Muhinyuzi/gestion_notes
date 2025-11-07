from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime

# ---------------- UTILISATEURS (Employés) ----------------
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)  # hashé
    type = Column(String(50), nullable=False, index=True)  # ex: employe
    equipe = Column(String(100), index=True)
    poste = Column(String(100), nullable=True)  # rôle ou poste de l'employé
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    date_embauche = Column(DateTime(timezone=True), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active = Column(Boolean, default=False)
    # 🆕 Champ pour la photo de profil
    avatar_url = Column(String(255), nullable=True)

    # Relations
    notes = relationship("Note", back_populates="auteur", cascade="all, delete-orphan")
    commentaires = relationship("Commentaire", back_populates="auteur", cascade="all, delete-orphan")


# 🔹 Index supplémentaires pour optimiser les requêtes fréquentes
Index("idx_utilisateur_email", Utilisateur.email)
Index("idx_utilisateur_nom", Utilisateur.nom)
