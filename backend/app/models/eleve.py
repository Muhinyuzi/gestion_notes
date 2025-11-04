from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime


# -------------------- Table principale Eleve --------------------
class Eleve(Base):
    __tablename__ = "eleves"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    adresse = Column(String, nullable=True)
    en_attente = Column(Boolean, default=True)
    actif = Column(Boolean, default=True)
    ferme = Column(Boolean, default=False)

    note_id = Column(Integer, ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
    date_note_assignee = Column(DateTime, nullable=True)  # <-- Nouveau champ

    # Traçabilité des utilisateurs
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relations
    note = relationship("Note", back_populates="eleves")
    creator = relationship("Utilisateur", foreign_keys=[created_by])
    updater = relationship("Utilisateur", foreign_keys=[updated_by]) 

# -------------------- Table d'historique Eleve --------------------
class EleveHistory(Base):
    __tablename__ = "eleves_history"

    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    edited_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    edited_at = Column(DateTime, default=datetime.utcnow)
    changes = Column(JSON)  # { "field_name": {"old": old_value, "new": new_value} }
    raison_changement = Column(String, nullable=True)  # <-- Nouveau champ pour stocker la raison

    eleve = relationship("Eleve", backref="history")
    editor = relationship("Utilisateur") 

# -------------------- Fonction utilitaire pour logger les changements --------------------
def log_eleve_change(session, eleve_id: int, user_id: int, changes: dict, raison_changement: str = None):
    """
    Enregistre une modification dans l'historique d'un élève.

    Args:
        session: Session SQLAlchemy active.
        eleve_id (int): ID de l'élève concerné.
        user_id (int): ID de l'utilisateur ayant fait la modification.
        changes (dict): Détails des changements, ex:
            {
                "adresse": {"old": "ancienne", "new": "nouvelle"},
                "note_id": {"old": 3, "new": 5}
            }
        raison_changement (str): Description du changement (facultatif).
    """
    history = EleveHistory(
        eleve_id=eleve_id,
        edited_by=user_id,
        edited_at=datetime.utcnow(),
        changes=changes,
        raison_changement=raison_changement or "Modification automatique"
    )
    session.add(history)
    session.commit()    


# 🔹 Index supplémentaires pour optimiser les requêtes fréquentes
Index("idx_eleve_note", Eleve.note_id)
Index("idx_eleve_actif", Eleve.actif)