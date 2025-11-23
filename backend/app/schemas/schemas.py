from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Generic, TypeVar
from datetime import datetime
from pydantic.generics import GenericModel

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

    # 🧩 Valeurs par défaut cohérentes avec le modèle SQLAlchemy
    equipe: Optional[str] = Field(default="Aucune", description="Équipe ou département de l'utilisateur")
    type: Optional[str] = Field(default="user", description="Rôle de l'utilisateur (admin, manager, user...)")

    poste: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    date_embauche: Optional[datetime] = None


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: Optional[str] = Field(default=None, description="Mot de passe (sera hashé)")


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
# 🔁 RÉSOLUTION DES RÉFÉRENCES CIRCULAIRES — Version propre et complète
# ======================================================

# Les modèles Pydantic s’utilisent souvent entre eux (ex: NoteOut → UtilisateurOut → NoteOut)
# Ces appels garantissent que toutes les références croisées sont bien reconstruites après définition.

FichierNoteBase.model_rebuild()
FichierNoteOut.model_rebuild()

UtilisateurBase.model_rebuild()
UtilisateurCreate.model_rebuild()
UtilisateurOut.model_rebuild()
UtilisateurDetailOut.model_rebuild()

NoteBase.model_rebuild()
NoteCreate.model_rebuild()
NoteOut.model_rebuild()
NoteDetailOut.model_rebuild()

CommentaireBase.model_rebuild()
CommentaireCreate.model_rebuild()
CommentaireOut.model_rebuild()

EleveBase.model_rebuild()
EleveCreate.model_rebuild()
EleveUpdate.model_rebuild()
EleveOut.model_rebuild()
EleveHistoryBase.model_rebuild()
EleveHistoryOut.model_rebuild()

EmailRequest.model_rebuild()

# ======================================================
# ✅ ENVELOPPE DE RÉPONSE GÉNÉRIQUE
# ======================================================
T = TypeVar("T")

class ResponseModel(GenericModel, Generic[T]):
    """Format de réponse uniforme pour toutes les routes API."""
    status: str = Field(..., example="success")
    data: Optional[T] = None


class PaginatedUsers(BaseModel):
    total: int
    page: int
    limit: int
    users: List[UtilisateurOut]    