from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.schemas import CommentaireCreate, CommentaireOut
from app.services.commentaires import add_commentaire_service

router = APIRouter()

@router.post("/notes/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(note_id: int, commentaire: CommentaireCreate, db: Session = Depends(get_db)):
    """
    Ajoute un commentaire à une note.
    """
    return add_commentaire_service(note_id, commentaire, db)