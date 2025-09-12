from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ======================================================
# Utilisateur
# ======================================================

class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    equipe: Optional[str] = None
    type: Optional[str] = None


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurOut(UtilisateurBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True


# ======================================================
# Note
# ======================================================

class NoteBase(BaseModel):
    titre: str
    contenu: str
    equipe: Optional[str] = None


class NoteCreate(NoteBase):
    auteur_id: int


class NoteOut(NoteBase):
    id: int
    date: datetime
    auteur: Optional[UtilisateurOut] = None

    class Config:
        orm_mode = True


# ======================================================
# Commentaire
# ======================================================

class CommentaireBase(BaseModel):
    contenu: str


class CommentaireCreate(CommentaireBase):
    auteur_id: int
    note_id: int


class CommentaireOut(CommentaireBase):
    id: int
    date: datetime
    auteur_id: int
    note_id: int
    auteur: Optional[UtilisateurOut] = None
    note: Optional[NoteOut] = None

    class Config:
        orm_mode = True


# ======================================================
# Relations imbriquées
# ======================================================

class NoteDetailOut(NoteOut):
    commentaires: List[CommentaireOut] = []


class UtilisateurDetailOut(UtilisateurOut):
    notes: List[NoteOut] = []
    commentaires: List[CommentaireOut] = []