from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

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
    auteur = relationship("Utilisateur", back_populates="notes")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=None, onupdate=func.now(), index=True)

    # Relations
    commentaires = relationship("Commentaire", back_populates="note", cascade="all, delete-orphan")
    fichiers = relationship("FichierNote", back_populates="note", cascade="all, delete-orphan")  # 🔹 fichiers multiples


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


# 🔹 Index supplémentaires pour optimiser les requêtes fréquentes
Index("idx_utilisateur_email", Utilisateur.email)
Index("idx_utilisateur_nom", Utilisateur.nom)
Index("idx_note_auteur", Note.auteur_id)
Index("idx_commentaire_auteur", Commentaire.auteur_id)
Index("idx_commentaire_note", Commentaire.note_id)
Index("idx_fichier_note", FichierNote.note_id)
