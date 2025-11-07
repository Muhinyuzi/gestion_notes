import pytest
from app.tests.conftest import TestingSessionLocal  # ✅ utilise la DB partagée
from app.models.note import Note
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import CommentaireCreate
from app.services.notes import (
    create_note_service,
    list_notes_service,
    get_note_detail_service,
    delete_note_service,
    like_note_service,
    add_commentaire_service,
    get_commentaires_service
)

# ==========================================================
# ⚙️ Fake utilisateur administrateur pour tests
# ==========================================================
class FakeAdmin:
    id = 0
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()

# ==========================================================
# 🧩 Fixture DB — utilise la même base que conftest.py
# ==========================================================
@pytest.fixture
def db(reset_db):  # dépend de la fixture reset_db du conftest
    """Fournit une session DB propre et partagée à chaque test"""
    db = TestingSessionLocal()

    # ✅ Crée un utilisateur admin test
    user = Utilisateur(
        nom="Admin",
        email="admin@test.com",
        mot_de_passe="hashed_test",
        type="admin",
        equipe="Dev"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # met à jour l’ID du fake user pour qu’il corresponde
    fake_admin.id = user.id

    yield db
    db.close()

# ==========================================================
# 🤖 Mock IA pour les résumés automatiques
# ==========================================================
@pytest.fixture(autouse=True)
def mock_ai(monkeypatch):
    def fake_summary(text: str):
        return "Résumé IA"
    monkeypatch.setattr("app.services.notes.generate_summary", fake_summary)

# ==========================================================
# 🧪 TESTS
# ==========================================================

def test_create_note_service(db):
    note = create_note_service(
        titre="Titre",
        contenu="Contenu de test",
        auteur_id=fake_admin.id,
        equipe="Dev",
        priorite="Haute",
        categorie="Info",
        fichiers=None,
        db=db,
        current_user=fake_admin
    )
    assert note.id is not None
    assert note.titre == "Titre"


def test_list_notes_service(db):
    create_note_service("Test", "Contenu", fake_admin.id, "Dev", None, None, None, db, fake_admin)
    result = list_notes_service("", "", "date_desc", 1, 20, db, fake_admin)
    assert result["total"] == 1
    assert len(result["notes"]) == 1


def test_get_note_detail_service(db):
    note = create_note_service("Titre", "C" * 200, fake_admin.id, "Dev", None, None, None, db, fake_admin)
    detail = get_note_detail_service(note.id, db)
    assert detail.id == note.id
    assert detail.resume_ia == "Résumé IA"
    assert detail.nb_vues == 1


def test_like_note_service(db):
    note = create_note_service("Titre", "Contenu", fake_admin.id, "Dev", None, None, None, db, fake_admin)
    response = like_note_service(note.id, db)
    assert response["likes"] == 1


def test_add_commentaire_service(db):
    note = create_note_service("Titre", "Contenu", fake_admin.id, "Dev", None, None, None, db, fake_admin)
    comment = add_commentaire_service(
        note.id,
        CommentaireCreate(contenu="Hello", auteur_id=fake_admin.id, note_id=note.id),
        db
    )
    assert comment.contenu == "Hello"


def test_get_commentaires_service(db):
    note = create_note_service("Titre", "Contenu", fake_admin.id, "Dev", None, None, None, db, fake_admin)
    add_commentaire_service(note.id, CommentaireCreate(contenu="Test", auteur_id=fake_admin.id, note_id=note.id), db)
    comments = get_commentaires_service(note.id, db)
    assert len(comments) == 1


def test_delete_note_service(db):
    note = create_note_service("Titre", "Contenu", fake_admin.id, "Dev", None, None, None, db, fake_admin)
    delete_note_service(note.id, db)
    assert db.query(Note).count() == 0
