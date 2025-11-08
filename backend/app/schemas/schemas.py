from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# ======================================================
# CONFIG GLOBALE — Compatible Pydantic v2+
# ======================================================
BaseModel.model_config = {"from_attributes": True}


# ======================================================
# UTILISATEUR (Employé)
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
    mot_de_passe: Optional[str] = None


class UtilisateurOut(UtilisateurBase):
    id: int
    date: Optional[datetime]
    mot_de_passe: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = False


# ======================================================
# FICHIER NOTE
# ======================================================
class FichierNoteBase(BaseModel):
    nom_fichier: str
    chemin: str


class FichierNoteOut(FichierNoteBase):
    id: int
    note_id: int


# ======================================================
# NOTE
# ======================================================
class NoteBase(BaseModel):
    titre: str
    contenu: str
    equipe: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = "Moyenne"
    resume_ia: Optional[str] = None


class NoteCreate(NoteBase):
    auteur_id: Optional[int] = None


class NoteOut(NoteBase):
    id: int
    likes: int
    nb_vues: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    auteur: Optional[UtilisateurOut] = None
    fichiers: Optional[List[FichierNoteOut]] = None
    eleves: Optional[List["EleveOut"]] = []  # 🔁 liens circulaires


class NoteDetailOut(NoteOut):
    commentaires: List["CommentaireOut"] = []


class NotesResponse(BaseModel):
    total: int
    page: int
    limit: int
    notes: List[NoteOut]


# ======================================================
# COMMENTAIRES
# ======================================================
class CommentaireBase(BaseModel):
    contenu: str


class CommentaireCreate(CommentaireBase):
    auteur_id: Optional[int] = None
    note_id: Optional[int] = None


class CommentaireOut(CommentaireBase):
    id: int
    date: datetime
    auteur_id: int
    note_id: int
    auteur: Optional[UtilisateurOut] = None
    note: Optional[NoteOut] = None


# ======================================================
# RELATIONS IMBRIQUÉES
# ======================================================
class UtilisateurDetailOut(UtilisateurOut):
    notes: List[NoteOut] = []
    commentaires: List[CommentaireOut] = []
    is_active: bool = False


# ======================================================
# ELEVES
# ======================================================
class EleveBase(BaseModel):
    nom: str
    prenom: str
    adresse: Optional[str] = None
    en_attente: Optional[bool] = True
    actif: Optional[bool] = True
    ferme: Optional[bool] = False
    note_id: Optional[int] = None


class EleveCreate(EleveBase):
    pass


class EleveUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    en_attente: Optional[bool] = None
    actif: Optional[bool] = None
    ferme: Optional[bool] = None
    note_id: Optional[int] = None
    updated_by: int  # ID de l'utilisateur qui met à jour


class EleveOut(EleveBase):
    id: int
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


class EleveHistoryBase(BaseModel):
    eleve_id: int
    edited_by: int
    edited_at: datetime
    changes: Dict[str, Dict[str, Optional[str]]]  # { "field": {"old": ..., "new": ...} }


class EleveHistoryOut(EleveHistoryBase):
    id: int


# ======================================================
# EMAIL REQUEST
# ======================================================
class EmailRequest(BaseModel):
    email: EmailStr


# ======================================================
# RÉSOLUTION DES RÉFÉRENCES CIRCULAIRES
# ======================================================
NoteDetailOut.model_rebuild()
UtilisateurDetailOut.model_rebuild()
CommentaireOut.model_rebuild()
NoteOut.model_rebuild()
EleveOut.model_rebuild()
EleveHistoryOut.model_rebuild()
EleveUpdate.model_rebuild()

