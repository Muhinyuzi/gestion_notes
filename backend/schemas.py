from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
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
    mot_de_passe: Optional[str] = None 

class UtilisateurOut(UtilisateurBase):
    id: int
    date: Optional[datetime]
    mot_de_passe: Optional[str] = None
    avatar_url: Optional[str] = None  # 🆕 lien vers l'avatar

    class Config:
        from_attributes = True  # ✅ Pydantic v2

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
        from_attributes = True

# ======================================================
# Note
# ======================================================
class NoteBase(BaseModel):
    titre: str
    contenu: str
    equipe: Optional[str] = None
    categorie: Optional[str] = None
    priorite: Optional[str] = "Moyenne"
    resume_ia: Optional[str] = None

class NoteCreate(NoteBase):
    auteur_id: int

class NoteOut(NoteBase):
    id: int
    likes: int
    nb_vues: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    auteur: Optional[UtilisateurOut] = None
    fichiers: Optional[List[FichierNoteOut]] = None
    # liste des élèves assignés (optionnelle)
    eleves: Optional[List["EleveOut"]] = []

    class Config:
        from_attributes = True

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
        from_attributes = True

# ======================================================
# Relations imbriquées
# ======================================================
class UtilisateurDetailOut(UtilisateurOut):
    notes: List[NoteOut] = []
    commentaires: List[CommentaireOut] = []

    class Config:
        from_attributes = True

# -------------------- Base Eleve --------------------
class EleveBase(BaseModel):
    nom: str
    prenom: str
    adresse: Optional[str] = None
    en_attente: Optional[bool] = True
    actif: Optional[bool] = True
    ferme: Optional[bool] = False
    note_id: Optional[int] = None

# -------------------- Création Eleve --------------------
class EleveCreate(EleveBase):
    pass

# -------------------- Mise à jour Eleve --------------------
class EleveUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    adresse: Optional[str] = None
    en_attente: Optional[bool] = None
    actif: Optional[bool] = None
    ferme: Optional[bool] = None
    note_id: Optional[int] = None
    updated_by: int  # ID de l'utilisateur qui met à jour

# -------------------- Lecture Eleve --------------------
class EleveOut(EleveBase):
    id: int
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# -------------------- Historique Eleve --------------------
class EleveHistoryBase(BaseModel):
    eleve_id: int
    edited_by: int
    edited_at: datetime
    changes: Dict[str, Dict[str, Optional[str]]]  # { "field": {"old": old_value, "new": new_value} }

class EleveHistoryOut(EleveHistoryBase):
    id: int

    class Config:
        from_attributes = True    

# 🔹 Résolution des références circulaires
NoteDetailOut.update_forward_refs()
UtilisateurDetailOut.update_forward_refs()
CommentaireOut.update_forward_refs()
NoteOut.update_forward_refs()
