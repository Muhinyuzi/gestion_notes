import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.db import Base
from app.models.utilisateur import Utilisateur
from app.models.note import Note
from app.services.eleves import (
    create_eleve_service,
    get_eleve_service,
    list_eleves_service,
    update_eleve_service,
    assign_note_service,
    unassign_note_service,
    get_eleve_history_service,
    delete_eleve_service
)
from app.schemas.schemas import EleveCreate, EleveUpdate

# ----------- Fake current user admin -----------
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()

# ----------- SQLite in-memory DB -----------
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()

    # seed admin user
    admin = Utilisateur(id=1, nom="Admin", email="admin@test.com", type="admin", equipe="Dev", mot_de_passe="pwd")
    db.add(admin)
    db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(engine)

# ==========================
# ✅ CREATE ELEVE
# ==========================
def test_create_eleve_service(db):
    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)
    assert eleve.nom == "A"
    assert eleve.created_by == 1

# ==========================
# ✅ GET ELEVE
# ==========================
def test_get_eleve_service(db):
    eleve = create_eleve_service(EleveCreate(nom="John", prenom="Doe"), fake_admin, db)
    got = get_eleve_service(eleve.id, db)
    assert got.nom == "John"

# ==========================
# ✅ LIST ELEVE
# ==========================
def test_list_eleves_service(db):
    create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)
    result = list_eleves_service(0, 10, db)
    assert len(result) == 1

# ==========================
# ✅ UPDATE ELEVE + HISTORY
# ==========================
def test_update_eleve_history(db):
    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)

    update_eleve_service(
        eleve.id,
        EleveUpdate(adresse="Rue X", updated_by=1),
        db
    )

    history = get_eleve_history_service(eleve.id, db)
    assert len(history) == 1
    assert history[0]["changes"]["adresse"]["new"] == "Rue X"

# ==========================
# ✅ ASSIGN NOTE
# ==========================
def test_assign_note(db):
    note = Note(titre="T", contenu="C", auteur_id=1, equipe="Dev")
    db.add(note); db.commit()

    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)
    updated = assign_note_service(eleve.id, note.id, fake_admin, db)
    assert updated.note_id == note.id

# ==========================
# ✅ UNASSIGN NOTE
# ==========================
def test_unassign_note(db):
    note = Note(titre="T", contenu="C", auteur_id=1, equipe="Dev")
    db.add(note); db.commit()

    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)
    assign_note_service(eleve.id, note.id, fake_admin, db)
    unassigned = unassign_note_service(eleve.id, fake_admin, db)
    assert unassigned.note_id is None

# ==========================
# ✅ GET HISTORY (not empty)
# ==========================
def test_get_eleve_history_service(db):
    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)

    update_eleve_service(
        eleve.id,
        EleveUpdate(adresse="Rue Test", updated_by=1),
        db
    )

    history = get_eleve_history_service(eleve.id, db)
    assert len(history) > 0

# ==========================
# ✅ DELETE ELEVE
# ==========================
def test_delete_eleve_service(db):
    eleve = create_eleve_service(EleveCreate(nom="A",prenom="B"), fake_admin, db)
    delete_eleve_service(eleve.id, fake_admin, db)

    with pytest.raises(Exception):
        get_eleve_service(eleve.id, db)


def test_assign_note_eleve_not_found_service(db):
    with pytest.raises(Exception):
        assign_note_service(999, 1, fake_admin, db)

def test_unassign_note_eleve_not_found_service(db):
    with pytest.raises(Exception):
        unassign_note_service(999, fake_admin, db)  

def test_update_eleve_not_found_service(db):
    with pytest.raises(Exception):
        update_eleve_service(999, EleveUpdate(adresse="X", updated_by=1), db)

def test_get_eleve_not_found_service(db):
    with pytest.raises(Exception):
        get_eleve_service(999, db)  
