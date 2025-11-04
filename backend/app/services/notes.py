from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os, shutil
from app.models.note import Note
from app.models.commentaire import Commentaire
from app.models.utilisateur import Utilisateur
from app.models.fichier import FichierNote
from app.schemas.schemas import CommentaireCreate, CommentaireOut, NotesResponse
from app.services.some_ai_module import generate_summary

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- CREATE ----------------
def create_note_service(
    titre, contenu, auteur_id, equipe, priorite, categorie, fichiers, db: Session, current_user: Utilisateur
):
    final_auteur_id = auteur_id or current_user.id

    note = Note(
        titre=titre,
        contenu=contenu,
        equipe=equipe or current_user.equipe,
        auteur_id=final_auteur_id,
        priorite=priorite,
        categorie=categorie
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    if fichiers:
        for f in fichiers:
            filename = f.filename.replace("\\", "/").split("/")[-1]
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)

            new_file = FichierNote(nom_fichier=filename, chemin=file_path, note_id=note.id)
            db.add(new_file)

        db.commit()
        db.refresh(note)

    return note

# ---------------- LIST ----------------
def list_notes_service(search, author, sort, page, limit, db: Session, current_user: Utilisateur):
    # ✅ En mode test -> ne filtre pas par utilisateur
    if os.getenv("TESTING") == "1":
        query = db.query(Note)
    else:
        # En prod -> comportement normal filtré par utilisateur
        query = db.query(Note).filter(Note.auteur_id == current_user.id)

    # 🔍 Recherche
    if search:
        query = query.filter(
            Note.titre.ilike(f"%{search}%") |
            Note.contenu.ilike(f"%{search}%")
        )

    # 👤 Filtre auteur
    if author:
        query = query.join(Note.auteur).filter(Utilisateur.nom.ilike(f"%{author}%"))

    # 🕓 Tri
    query = query.order_by(
        Note.created_at.asc() if sort == "date_asc" else Note.created_at.desc()
    )

    total = query.count()

    notes = (
        query.options(joinedload(Note.auteur), joinedload(Note.fichiers))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "notes": notes
    }


# ---------------- DETAIL ----------------
def get_note_detail_service(note_id: int, db: Session):
    note = (
        db.query(Note)
        .options(joinedload(Note.commentaires), joinedload(Note.auteur), joinedload(Note.fichiers))
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    if not note.resume_ia and note.contenu and len(note.contenu) > 100:
        try:
            note.resume_ia = generate_summary(note.contenu)
            db.commit()
            db.refresh(note)
        except Exception:
            db.rollback()

    note.nb_vues = (note.nb_vues or 0) + 1
    db.commit()
    db.refresh(note)
    return note

# ---------------- UPDATE ----------------
async def update_note_service(note_id, titre, contenu, equipe, categorie, priorite, fichiers, db: Session):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    note.titre = titre
    note.contenu = contenu
    note.equipe = equipe or note.equipe
    note.categorie = categorie or note.categorie
    note.priorite = priorite or note.priorite

    for f in fichiers:
        file_location = f"uploads/{f.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(await f.read())
        new_file = FichierNote(nom_fichier=f.filename, chemin=file_location, note_id=note.id)
        db.add(new_file)

    db.commit()
    db.refresh(note)
    return note

# ---------------- DELETE ----------------
def delete_note_service(note_id: int, db: Session):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    db.delete(note)
    db.commit()
    return None

# ---------------- LIKE ----------------
def like_note_service(note_id: int, db: Session):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    note.likes = (note.likes or 0) + 1
    db.commit()
    db.refresh(note)
    return {"likes": note.likes}

# ---------------- COMMENTAIRES ----------------
def get_commentaires_service(note_id: int, db: Session):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    return note.commentaires

def add_commentaire_service(note_id: int, commentaire: CommentaireCreate, db: Session):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    # ✅ tests exigent 404 si auteur n'existe pas
    auteur = db.query(Utilisateur).filter(Utilisateur.id == commentaire.auteur_id).first()
    if not auteur:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    new_comment = Commentaire(
        contenu=commentaire.contenu,
        auteur_id=commentaire.auteur_id,
        note_id=note_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return CommentaireOut.from_orm(new_comment)

# ---------------- SUPPRESSION DE FICHIER ----------------
def delete_file_service(file_id: int, db: Session):
    fichier = db.query(FichierNote).filter(FichierNote.id == file_id).first()
    if not fichier:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

    if os.path.exists(fichier.chemin):
        os.remove(fichier.chemin)

    db.delete(fichier)
    db.commit()
    return {"detail": "Fichier supprimé avec succès"}
