# app/tests/test_router_notes.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db
from app.auth import get_current_user
from app.models.utilisateur import Utilisateur

# ✅ Test DB (sqlite file, not memory, because TestClient needs persistence)
engine = create_engine("sqlite:///./test_router_notes.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# ✅ Override database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ✅ Fake admin user
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

def override_get_current_user():
    return FakeAdmin()

app.dependency_overrides[get_current_user] = override_get_current_user

# ✅ Setup DB
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create admin in DB
    db = TestingSessionLocal()
    db.add(Utilisateur(id=1, nom="Admin", email="admin@test.com", type="admin", equipe="Dev", mot_de_passe="test"))
    db.commit()
    db.close()
    yield

client = TestClient(app)

# -----------------------------------------------------------------
# ✅ TEST CREATE NOTE
# -----------------------------------------------------------------
def test_create_note_router():
    data = {
        "titre": "Note Test",
        "contenu": "Contenu Test",
        "auteur_id": 1,
        "equipe": "Dev",
        "priorite": "haute",
        "categorie": "info"
    }
    r = client.post("/notes/", data=data)
    assert r.status_code == 200
    res = r.json()
    assert res["titre"] == "Note Test"

# -----------------------------------------------------------------
# ✅ TEST LIST NOTES
# -----------------------------------------------------------------
def test_list_notes_router():
    test_create_note_router()  # Create
    r = client.get("/notes/")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert len(data["notes"]) == 1

# -----------------------------------------------------------------
# ✅ TEST DETAIL
# -----------------------------------------------------------------
def test_get_note_detail_router():
    create = client.post("/notes/", data={"titre":"A","contenu":"B"*200,"auteur_id":1})
    note_id = create.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["id"] == note_id

# -----------------------------------------------------------------
# ✅ TEST LIKE NOTE
# -----------------------------------------------------------------
def test_like_note_router():
    create = client.post("/notes/", data={"titre":"L","contenu":"c","auteur_id":1})
    note_id = create.json()["id"]

    r = client.post(f"/notes/{note_id}/like")
    assert r.status_code == 200
    assert r.json()["likes"] == 1

# -----------------------------------------------------------------
# ✅ TEST COMMENTS
# -----------------------------------------------------------------
def test_add_commentaire_router():
    create = client.post("/notes/", data={"titre":"C","contenu":"text","auteur_id":1})
    note_id = create.json()["id"]

    commentaire = {"contenu":"Salut","auteur_id":1,"note_id":note_id}
    r = client.post(f"/notes/{note_id}/commentaires", json=commentaire)

    assert r.status_code == 200
    assert r.json()["contenu"] == "Salut"

def test_get_commentaires_router():
    create = client.post("/notes/", data={"titre":"C","contenu":"text","auteur_id":1})
    note_id = create.json()["id"]

    client.post(f"/notes/{note_id}/commentaires",
                json={"contenu":"Test","auteur_id":1,"note_id":note_id})

    r = client.get(f"/notes/{note_id}/commentaires")
    assert r.status_code == 200
    assert len(r.json()) == 1

# -----------------------------------------------------------------
# ✅ TEST DELETE NOTE
# -----------------------------------------------------------------
def test_delete_note_router():
    create = client.post("/notes/", data={"titre":"D","contenu":"z","auteur_id":1})
    note_id = create.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
