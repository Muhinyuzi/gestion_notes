# app/tests/test_service_commentaires.py
import pytest
from app.tests.conftest import TestingSessionLocal
from app.models.note import Note
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import CommentaireCreate
from app.services.commentaires import add_commentaire_service, get_commentaires_service

@pytest.fixture
def db():
    db = TestingSessionLocal()
    # Crée un utilisateur et une note
    user = Utilisateur(
        nom="Alice",
        email="alice@test.com",
        mot_de_passe="12345678",
        type="admin",
        equipe="Dev"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    note = Note(
        titre="Note test",
        contenu="Contenu test",
        auteur_id=user.id,
        equipe="Dev"
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    yield db
    db.close()

def test_add_commentaire_service(db):
    """✅ Test ajout de commentaire"""
    note = db.query(Note).first()
    user = db.query(Utilisateur).first()

    data = CommentaireCreate(contenu="Super note!", auteur_id=user.id, note_id=note.id)
    commentaire = add_commentaire_service(note.id, data, db)

    assert commentaire.contenu == "Super note!"
    assert commentaire.auteur_id == user.id
    assert commentaire.note_id == note.id

def test_get_commentaires(db):
    """✅ Test récupération des commentaires"""
    note = db.query(Note).first()
    user = db.query(Utilisateur).first()
    data = CommentaireCreate(contenu="Très bien", auteur_id=user.id, note_id=note.id)
    add_commentaire_service(note.id, data, db)

    commentaires = get_commentaires_service(note.id, db)
    assert len(commentaires) == 1
    assert commentaires[0].contenu == "Très bien"
