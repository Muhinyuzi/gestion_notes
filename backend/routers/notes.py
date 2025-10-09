from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import shutil
from db import get_db
from models import Note, Utilisateur, Commentaire, FichierNote
from schemas import NoteOut, NoteDetailOut, FichierNoteOut, CommentaireOut, NotesResponse
from auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- CREATE NOTE ----------------
@router.post("/", response_model=NoteOut)
def create_note(
    note_data: dict,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    note = Note(
        titre=note_data.get("titre"),
        contenu=note_data.get("contenu"),
        equipe=current_user.equipe,  # ⚡ équipe de l'utilisateur
        auteur_id=current_user.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

# ---------------- LIST NOTES ----------------
@router.get("/", response_model=NotesResponse)
def list_notes(
    search: str = Query("", description="Mot-clé"),
    author: str = Query("", description="Nom auteur"),
    sort: str = Query("date_desc", description="date_asc ou date_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Si admin → toutes les notes
    Sinon → seulement les notes de son équipe
    """
    query = db.query(Note).options(joinedload(Note.auteur), joinedload(Note.fichiers))

    # 🔒 Filtre selon rôle
    if current_user.type != "admin":
        if not current_user.equipe:
            raise HTTPException(status_code=400, detail="L'utilisateur n'est pas associé à une équipe.")
        query = query.filter(Note.equipe == current_user.equipe)

    # 🔍 Filtres facultatifs
    if search:
        query = query.filter(Note.titre.ilike(f"%{search}%") | Note.contenu.ilike(f"%{search}%"))
    if author:
        query = query.join(Note.auteur).filter(Utilisateur.nom.ilike(f"%{author}%"))

    # 🧮 Tri
    query = query.order_by(Note.created_at.asc() if sort == "date_asc" else Note.created_at.desc())

    # 📄 Pagination
    total = query.count()
    notes = query.offset((page - 1) * limit).limit(limit).all()

    return {"total": total, "page": page, "limit": limit, "notes": notes}


# ---------------- DETAIL NOTE ----------------
@router.get("/{note_id}", response_model=NoteDetailOut)
def get_note_detail(note_id: int, db: Session = Depends(get_db)):
    note = (
        db.query(Note)
        .options(
            joinedload(Note.commentaires),
            joinedload(Note.auteur),
            joinedload(Note.fichiers)
        )
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    return note

# ---------------- UPDATE NOTE ----------------
@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_data: dict, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    note.titre = note_data.get("titre", note.titre)
    note.contenu = note_data.get("contenu", note.contenu)
    note.equipe = note_data.get("equipe", note.equipe)
    db.commit()
    db.refresh(note)
    return note

# ---------------- DELETE NOTE ----------------
@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    db.delete(note)
    db.commit()
    return None

# ---------------- GET COMMENTAIRES ----------------
@router.get("/{note_id}/commentaires", response_model=List[CommentaireOut])
def get_commentaires(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    return note.commentaires

# ---------------- ADD COMMENTAIRE ----------------
@router.post("/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(note_id: int, commentaire: CommentaireOut, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    new_comment = Commentaire(
        contenu=commentaire.contenu,
        auteur_id=commentaire.auteur_id,
        note_id=note_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment
