from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base
from datetime import datetime

# ---------------- UTILISATEURS (Employés) ----------------
class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)  # hashé
    type = Column(String(50), nullable=False, index=True)  # ex: employe
    equipe = Column(String(100), index=True)
    poste = Column(String(100), nullable=True)  # rôle ou poste de l'employé
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    date_embauche = Column(DateTime(timezone=True), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # 🆕 Champ pour la photo de profil
    avatar_url = Column(String(255), nullable=True)

    # Relations
    notes = relationship("Note", back_populates="auteur", cascade="all, delete-orphan")
    commentaires = relationship("Commentaire", back_populates="auteur", cascade="all, delete-orphan")


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


# ---------------- FICHIERS DES NOTES ----------------
class FichierNote(Base):
    __tablename__ = "fichiers_notes"

    id = Column(Integer, primary_key=True, index=True)
    nom_fichier = Column(String(255), nullable=False)
    chemin = Column(String(255), nullable=False)

    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"))
    note = relationship("Note", back_populates="fichiers")


# ---------------- COMMENTAIRES ----------------
class Commentaire(Base):
    __tablename__ = "commentaires"

    id = Column(Integer, primary_key=True, index=True)
    contenu = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    auteur_id = Column(Integer, ForeignKey("utilisateurs.id", ondelete="CASCADE"), index=True)
    auteur = relationship("Utilisateur", back_populates="commentaires")

    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    note = relationship("Note", back_populates="commentaires")

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
Index("idx_utilisateur_email", Utilisateur.email)
Index("idx_utilisateur_nom", Utilisateur.nom)
Index("idx_note_auteur", Note.auteur_id)
Index("idx_commentaire_auteur", Commentaire.auteur_id)
Index("idx_commentaire_note", Commentaire.note_id)
Index("idx_fichier_note", FichierNote.note_id)
Index("idx_eleve_note", Eleve.note_id)
Index("idx_eleve_actif", Eleve.actif)
