# app/api/v1/notes.py
from fastapi import APIRouter, Depends, Form, File, UploadFile, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import NoteOut, NoteDetailOut, NotesResponse, CommentaireOut, CommentaireCreate
from app.services.notes import (
    create_note_service,
    list_notes_service,
    get_note_detail_service,
    update_note_service,
    delete_note_service,
    like_note_service,
    get_commentaires_service,
    add_commentaire_service,
    delete_file_service,
)
from app.auth import get_current_user

router = APIRouter()

# ---------------- CREATE ----------------
@router.post("/", response_model=NoteOut)
def create_note(
    titre: str = Form(...),
    contenu: str = Form(...),
    auteur_id: int = Form(...),
    equipe: Optional[str] = Form(None),
    priorite: Optional[str] = Form("moyenne"),
    categorie: Optional[str] = Form(None),
    fichiers: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return create_note_service(
        titre, contenu, auteur_id, equipe, priorite, categorie, fichiers, db, current_user
    )

# ---------------- LIST ----------------
@router.get("/", response_model=NotesResponse)
def list_notes(
    search: str = Query("", description="Mot-clé"),
    author: str = Query("", description="Nom auteur"),
    sort: str = Query("date_desc", description="date_asc ou date_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return list_notes_service(search, author, sort, page, limit, db, current_user)

# ---------------- DETAIL ----------------
@router.get("/{note_id}", response_model=NoteDetailOut)
def get_note_detail(note_id: int, db: Session = Depends(get_db)):
    return get_note_detail_service(note_id, db)

# ---------------- UPDATE ----------------
@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: int,
    titre: str = Form(...),
    contenu: str = Form(...),
    equipe: Optional[str] = Form(None),
    categorie: Optional[str] = Form(None),
    priorite: Optional[str] = Form(None),
    fichiers: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):
    return await update_note_service(note_id, titre, contenu, equipe, categorie, priorite, fichiers, db)

# ---------------- DELETE ----------------
@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    return delete_note_service(note_id, db)

# ---------------- LIKE ----------------
@router.post("/{note_id}/like")
def like_note(note_id: int, db: Session = Depends(get_db)):
    return like_note_service(note_id, db)

# ---------------- COMMENTAIRES ----------------
@router.get("/{note_id}/commentaires", response_model=List[CommentaireOut])
def get_commentaires(note_id: int, db: Session = Depends(get_db)):
    return get_commentaires_service(note_id, db)

@router.post("/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(note_id: int, commentaire: CommentaireCreate, db: Session = Depends(get_db)):
    return add_commentaire_service(note_id, commentaire, db)

# ---------------- SUPPRESSION DE FICHIER ----------------
@router.delete("/fichiers/{file_id}", response_model=dict)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    return delete_file_service(file_id, db)
