# app/tests/test_service_notes.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.note import Note
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import CommentaireCreate
from app.services.notes import (
    create_note_service,
    list_notes_service,
    get_note_detail_service,
    update_note_service,
    delete_note_service,
    like_note_service,
    add_commentaire_service,
    get_commentaires_service
)

# ✅ Fake current user
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()

# ✅ SQLite In-Memory DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    # create test user in db
    user = Utilisateur(id=1, nom="Admin", email="admin@test.com", type="admin", equipe="Dev", mot_de_passe="test")
    db.add(user)
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(engine)

# ✅ Mock generate_summary()
@pytest.fixture(autouse=True)
def mock_ai(monkeypatch):
    def fake_summary(text: str):
        return "Résumé IA"
    monkeypatch.setattr("app.services.notes.generate_summary", fake_summary)

# -----------------------------------------
# ✅ TEST CREATE NOTE
# -----------------------------------------
def test_create_note_service(db):
    note = create_note_service(
        titre="Titre",
        contenu="Contenu de test",
        auteur_id=1,
        equipe="Dev",
        priorite="Haute",
        categorie="Info",
        fichiers=None,
        db=db,
        current_user=fake_admin
    )
    assert note.id is not None
    assert note.titre == "Titre"

# -----------------------------------------
# ✅ TEST LIST NOTES
# -----------------------------------------
def test_list_notes_service(db):
    create_note_service("Test", "Contenu", 1, "Dev", None, None, None, db, fake_admin)

    result = list_notes_service("", "", "date_desc", 1, 20, db, fake_admin)
    assert result["total"] == 1
    assert len(result["notes"]) == 1

# -----------------------------------------
# ✅ TEST DETAIL NOTE (w/ AI summary & views)
# -----------------------------------------
def test_get_note_detail_service(db):
    note = create_note_service("Titre", "C" * 200, 1, "Dev", None, None, None, db, fake_admin)

    detail = get_note_detail_service(note.id, db)
    assert detail.id == note.id
    assert detail.resume_ia == "Résumé IA"
    assert detail.nb_vues == 1

# -----------------------------------------
# ✅ TEST LIKE NOTE
# -----------------------------------------
def test_like_note_service(db):
    note = create_note_service("Titre", "Contenu", 1, "Dev", None, None, None, db, fake_admin)
    response = like_note_service(note.id, db)
    assert response["likes"] == 1

# -----------------------------------------
# ✅ TEST COMMENTS
# -----------------------------------------
def test_add_commentaire_service(db):
    note = create_note_service("Titre", "Contenu", 1, "Dev", None, None, None, db, fake_admin)
    comment = add_commentaire_service(
        note.id,
        CommentaireCreate(contenu="Hello", auteur_id=1, note_id=note.id),
        db
    )
    assert comment.contenu == "Hello"

# -----------------------------------------
# ✅ TEST GET COMMENTS LIST
# -----------------------------------------
def test_get_commentaires_service(db):
    note = create_note_service("Titre", "Contenu", 1, "Dev", None, None, None, db, fake_admin)
    add_commentaire_service(note.id, CommentaireCreate(contenu="Test", auteur_id=1, note_id=note.id), db)
    comments = get_commentaires_service(note.id, db)
    assert len(comments) == 1

# -----------------------------------------
# ✅ TEST DELETE NOTE
# -----------------------------------------
def test_delete_note_service(db):
    note = create_note_service("Titre", "Contenu", 1, "Dev", None, None, None, db, fake_admin)
    delete_note_service(note.id, db)
    assert db.query(Note).count() == 0
