# app/services/commentaires.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.commentaire import Commentaire
from app.models.note import Note
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import CommentaireCreate, CommentaireOut

def add_commentaire_service(note_id: int, commentaire: CommentaireCreate, db: Session):
    # ✅ Vérifie si l'auteur existe AVANT la note (conformité aux tests)
    auteur = db.query(Utilisateur).filter(Utilisateur.id == commentaire.auteur_id).first()
    if not auteur:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    # ✅ Vérifie si la note existe
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    # Crée le commentaire
    new_comment = Commentaire(
        contenu=commentaire.contenu,
        auteur_id=commentaire.auteur_id,
        note_id=note_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return CommentaireOut.model_validate(new_comment)

def get_commentaires_service(note_id: int, db: Session):
    """
    Retourne la liste des commentaires liés à une note.
    """
    commentaires = (
        db.query(Commentaire)
        .filter(Commentaire.note_id == note_id)
        .order_by(Commentaire.id.asc())
        .all()
    )
    return [CommentaireOut.model_validate(c) for c in commentaires]
