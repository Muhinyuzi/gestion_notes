# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------- Utilisateur ----------
class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    equipe: Optional[str] = None

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurOut(UtilisateurBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

# ---------- Note ----------
class NoteBase(BaseModel):
    titre: str
    contenu: str
    equipe: Optional[str] = None

class NoteCreate(NoteBase):
    auteur_id: int

class NoteOut(BaseModel):
    id: int
    titre: str
    contenu: str
    equipe: Optional[str] = None
    date: datetime
    auteur: Optional[UtilisateurOut] = None   # 👈 propre, pas "auteur_obj"

    class Config:
        orm_mode = True

       

# ---------- Commentaire ----------
class CommentaireBase(BaseModel):
    contenu: str


class CommentaireCreate(CommentaireBase):
    auteur_id: int
    note_id: int   # 👈 il faut savoir à quelle note rattacher le commentaire


class CommentaireOut(CommentaireBase):
    id: int
    auteur_id: int
    note_id: int
    date: datetime

    # Relations
    auteur: Optional[UtilisateurOut] = None  # 👈 pour avoir nom/email de l’auteur
    note: Optional[NoteOut] = None           # 👈 pour avoir titre de la note

    class Config:
        orm_mode = True

class NoteDetailOut(BaseModel):
    id: int
    titre: str
    contenu: str
    equipe: Optional[str] = None
    date: datetime
    auteur: Optional[UtilisateurOut] = None
    commentaires: List[CommentaireOut] = []

    class Config:
        orm_mode = True          

       