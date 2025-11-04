import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.utilisateur import Utilisateur
from app.models.note import Note
from app.services.commentaires import add_commentaire_service
from app.schemas.schemas import CommentaireCreate


# ✅ SQLite In-Memory DB pour tests
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()

    # Seed utilisateur + note
    user = Utilisateur(id=1, nom="Test", email="test@test.com", mot_de_passe="pass", equipe="Dev", type="admin")
    note = Note(id=1, titre="Titre", contenu="Contenu", auteur_id=1, equipe="Dev")

    db.add(user)
    db.add(note)
    db.commit()
    yield db

    db.close()
    Base.metadata.drop_all(engine)


# ✅ Test : ajout commentaire OK
def test_add_commentaire_service_success(db):
    data = CommentaireCreate(contenu="Super note!", auteur_id=1)

    result = add_commentaire_service(1, data, db)

    assert result.contenu == "Super note!"
    assert result.auteur_id == 1
    assert result.note_id == 1


# ❌ Test : note inexistante
def test_add_commentaire_service_note_not_found(db):
    data = CommentaireCreate(contenu="Hello", auteur_id=1)

    with pytest.raises(Exception) as exc:
        add_commentaire_service(99, data, db)

    assert "Note non trouvée" in str(exc.value)


# ❌ Test : auteur inexistant
def test_add_commentaire_service_author_not_found(db):
    data = CommentaireCreate(contenu="Hello", auteur_id=999)

    with pytest.raises(Exception) as exc:
        add_commentaire_service(1, data, db)

    assert "Auteur non trouvé" in str(exc.value)
