# routers/notes_router.py (remplace/complète ton fichier existant)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os, shutil
from db import get_db
from models import Note, Utilisateur, Commentaire, FichierNote
from schemas import NoteOut, NoteDetailOut, CommentaireOut, NotesResponse, CommentaireCreate
from auth import get_current_user
from some_ai_module import generate_summary

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CREATE
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
    current_user: Utilisateur = Depends(get_current_user)
):
    # Création de la note principale
    note = Note(
        titre=titre,
        contenu=contenu,
        equipe=equipe or current_user.equipe,
        auteur_id=current_user.id,
        priorite=priorite,
        categorie=categorie
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # Gestion des fichiers uploadés
    if fichiers:
        for f in fichiers:
            filename = f.filename.replace("\\", "/").split("/")[-1]
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)

            new_file = FichierNote(
                nom_fichier=filename,
                chemin=file_path,
                note_id=note.id
            )
            db.add(new_file)

        db.commit()
        db.refresh(note)

    return note


# LIST
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
    query = db.query(Note).options(joinedload(Note.auteur), joinedload(Note.fichiers))
    if current_user.type != "admin":
        if not current_user.equipe:
            raise HTTPException(status_code=400, detail="L'utilisateur n'est pas associé à une équipe.")
        query = query.filter(Note.equipe == current_user.equipe)
    if search:
        query = query.filter(Note.titre.ilike(f"%{search}%") | Note.contenu.ilike(f"%{search}%"))
    if author:
        query = query.join(Note.auteur).filter(Utilisateur.nom.ilike(f"%{author}%"))
    query = query.order_by(Note.created_at.asc() if sort == "date_asc" else Note.created_at.desc())
    total = query.count()
    notes = query.offset((page - 1) * limit).limit(limit).all()
    for n in notes:
        for fichier in n.fichiers:
            if isinstance(fichier.chemin, bytes):
                fichier.chemin = fichier.chemin.decode("utf-8", errors="ignore")
    return {"total": total, "page": page, "limit": limit, "notes": notes}

# DETAIL
@router.get("/{note_id}", response_model=NoteDetailOut)
def get_note_detail(note_id: int, db: Session = Depends(get_db)):
    note = (
        db.query(Note)
        .options(joinedload(Note.commentaires), joinedload(Note.auteur), joinedload(Note.fichiers))
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    # nettoyer chemins
    for f in note.fichiers:
        if isinstance(f.chemin, bytes):
            f.chemin = f.chemin.decode("utf-8", errors="ignore")

    # résumé IA (asynchrone possible — ici sync simple)
    if not note.resume_ia and note.contenu and len(note.contenu) > 100:
        try:
            note.resume_ia = generate_summary(note.contenu)
            db.commit()
            db.refresh(note)
        except Exception:
            # ne pas bloquer l'utilisateur si l'IA échoue
            db.rollback()

    # incrémenter vues
    note.nb_vues = (note.nb_vues or 0) + 1
    db.commit()
    db.refresh(note)

    return note

# UPDATE 
@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: int,
    titre: str = Form(...),
    contenu: str = Form(...),
    equipe: Optional[str] = Form(None),
    categorie: Optional[str] = Form(None),
    priorite: Optional[str] = Form(None),
    fichiers: List[UploadFile] = File([]),  # liste de fichiers
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    # Mise à jour des champs
    note.titre = titre
    note.contenu = contenu
    note.equipe = equipe or note.equipe
    note.categorie = categorie or note.categorie
    note.priorite = priorite or note.priorite

    # Sauvegarder les fichiers sur disque ou en DB
    for f in fichiers:
        file_location = f"uploads/{f.filename}"  # par exemple
        with open(file_location, "wb") as buffer:
            buffer.write(await f.read())
        # créer l'objet FichierNote lié à la note
        new_file = FichierNote(nom_fichier=f.filename, chemin=file_location, note_id=note.id)
        db.add(new_file)

    db.commit()
    db.refresh(note)
    return note

# DELETE
@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    db.delete(note)
    db.commit()
    return None

# LIKE
@router.post("/{note_id}/like")
def like_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    note.likes = (note.likes or 0) + 1
    db.commit()
    db.refresh(note)
    return {"likes": note.likes}

# ---------------- GET COMMENTAIRES ----------------
@router.get("/{note_id}/commentaires", response_model=List[CommentaireOut])
def get_commentaires(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    return note.commentaires

# ---------------- ADD COMMENTAIRE ----------------
@router.post("/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(note_id: int, commentaire: CommentaireCreate, db: Session = Depends(get_db)):
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


# ---------------- SUPPRIMER UN FICHIER ----------------
@router.delete("/fichiers/{file_id}", response_model=dict)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    fichier = db.query(FichierNote).filter(FichierNote.id == file_id).first()
    if not fichier:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Supprimer le fichier physique du disque
    if os.path.exists(fichier.chemin):
        os.remove(fichier.chemin)

    # Supprimer l'entrée en base
    db.delete(fichier)
    db.commit()

    return {"detail": "Fichier supprimé avec succès"}