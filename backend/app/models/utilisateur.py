from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime


class Utilisateur(Base):
    """
    Modèle représentant un utilisateur / employé du système.
    Inclut les informations d'identité, de poste et d'appartenance d'équipe.
    """
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)  # mot de passe hashé

    # 🧩 Type / rôle de l'utilisateur (avec valeur par défaut logique)
    type = Column(
        String(50),
        nullable=False,
        index=True,
        server_default="user",  # ✅ pas de migration nécessaire
        doc="Rôle de l'utilisateur (admin, manager, user, viewer, etc.)"
    )

    # 👥 Équipe / Département (avec default 'Aucune')
    equipe = Column(
        String(100),
        nullable=True,
        index=True,
        server_default="Aucune",
        doc="Équipe ou département de l'utilisateur (ex: Dev, RH, Support...)"
    )

    poste = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    date_embauche = Column(DateTime(timezone=True), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active = Column(Boolean, default=False)
    avatar_url = Column(String(255), nullable=True)

    # 🔗 Relations ORM
    notes = relationship("Note", back_populates="auteur", cascade="all, delete-orphan")
    commentaires = relationship("Commentaire", back_populates="auteur", cascade="all, delete-orphan")

    # ⚙️ Contraintes et index supplémentaires
    __table_args__ = (
        UniqueConstraint("email", name="uq_utilisateur_email"),
        Index("idx_utilisateur_nom", "nom"),
        Index("idx_utilisateur_type", "type"),
        Index("idx_utilisateur_equipe", "equipe"),
    )

    def __repr__(self):
        return f"<Utilisateur(id={self.id}, nom='{self.nom}', type='{self.type}', equipe='{self.equipe}')>"
