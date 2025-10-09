from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ======================================================
# Utilisateur (Employé)
# ======================================================
class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    equipe: Optional[str] = None
    type: Optional[str] = None
    poste: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    date_embauche: Optional[datetime] = None

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurOut(UtilisateurBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

# ======================================================
# FichierNote
# ======================================================
class FichierNoteBase(BaseModel):
    nom_fichier: str
    chemin: str

class FichierNoteOut(FichierNoteBase):
    id: int
    note_id: int

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
    created_at: datetime
    updated_at: Optional[datetime] = None
    auteur: Optional[UtilisateurOut] = None
    fichiers: Optional[List[FichierNoteOut]] = []

    class Config:
        orm_mode = True

class NoteDetailOut(NoteOut):
    commentaires: List["CommentaireOut"] = []

class NotesResponse(BaseModel):
    total: int
    page: int
    limit: int
    notes: List[NoteOut]    

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
class UtilisateurDetailOut(UtilisateurOut):
    notes: List[NoteOut] = []
    commentaires: List[CommentaireOut] = []

# 🔹 Résolution des références circulaires
NoteDetailOut.update_forward_refs()
UtilisateurDetailOut.update_forward_refs()
CommentaireOut.update_forward_refs()
