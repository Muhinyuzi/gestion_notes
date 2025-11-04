from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.schemas import CommentaireCreate, CommentaireOut
from app.services.commentaires import add_commentaire_service
from app.models.utilisateur import Utilisateur
from app.models.note import Note
from app.auth import get_current_user
router = APIRouter()

@router.post("/notes/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(
    note_id: int,
    commentaire: CommentaireCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    auteur_id = commentaire.auteur_id if commentaire.auteur_id is not None else current_user.id

    data = CommentaireCreate(
        contenu=commentaire.contenu,
        auteur_id=auteur_id,
        note_id=note_id
    )
    return add_commentaire_service(note_id, data, db)

def test_create_comment_missing_content(client, create_test_user):
    note = client.post("/notes/", json={
        "titre": "N", "contenu": "C", "auteur_id": create_test_user["id"]
    }).json()

    r = client.post(f"/notes/{note['id']}/commentaires", json={"auteur_id": create_test_user["id"]})
    assert r.status_code == 422

def test_create_comment_missing_author(client, create_test_user):
    note = client.post("/notes/", json={
        "titre": "N", "contenu": "C", "auteur_id": create_test_user["id"]
    }).json()

    r = client.post(f"/notes/{note['id']}/commentaires", json={"contenu": "No author"})
    assert r.status_code == 200
    assert r.json()["auteur_id"] == create_test_user["id"]  

def test_create_comment_note_not_found(client, create_test_user):
    r = client.post("/notes/9999/commentaires", json={
        "contenu": "Hello", "auteur_id": create_test_user["id"]
    })
    assert r.status_code == 404     
