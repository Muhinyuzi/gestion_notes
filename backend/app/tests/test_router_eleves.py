# app/tests/test_router_eleves.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db
from app.models.utilisateur import Utilisateur
from app.models.note import Note
from app.auth import get_current_user

# ✅ SQLite test DB
engine = create_engine("sqlite:///./test_router_eleves.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# ✅ Override DB dependency
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

client = TestClient(app)

# ✅ Setup DB + seed admin
@pytest.fixture(autouse=True)
def setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    admin = Utilisateur(id=1, nom="Admin", email="admin@test.com", type="admin", equipe="Dev", mot_de_passe="pass")
    db.add(admin)
    db.commit()
    db.close()
    yield

# ----------------------------------------------------------------
# ✅ CREATE ELEVE
# ----------------------------------------------------------------
def test_create_eleve():
    eleve = {
        "nom": "Jean",
        "prenom": "Claude",
        "adresse": "Rue Test",
        "actif": True,
        "en_attente": False,
        "ferme": False
    }

    r = client.post("/eleves/", json=eleve)
    assert r.status_code == 200, r.text
    assert r.json()["nom"] == "Jean"

# ----------------------------------------------------------------
# ✅ GET ELEVE
# ----------------------------------------------------------------
def test_get_eleve():
    res = client.post("/eleves/", json={"nom":"A","prenom":"B"})
    eleve_id = res.json()["id"]

    r = client.get(f"/eleves/{eleve_id}")
    assert r.status_code == 200
    assert r.json()["id"] == eleve_id

# ----------------------------------------------------------------
# ✅ LIST ELEVE
# ----------------------------------------------------------------
def test_list_eleves():
    client.post("/eleves/", json={"nom":"A","prenom":"B"})
    r = client.get("/eleves/")
    assert r.status_code == 200
    assert len(r.json()) == 1

# ----------------------------------------------------------------
# ✅ UPDATE ELEVE
# ----------------------------------------------------------------
def test_update_eleve():
    res = client.post("/eleves/", json={"nom":"A","prenom":"B"})
    eleve_id = res.json()["id"]

    r = client.put(
    f"/eleves/{eleve_id}",
    json={
        "nom": "A",
        "prenom": "B",
        "adresse": "Nouvelle Rue"
    }
)
    assert r.status_code == 200
    assert r.json()["adresse"] == "Nouvelle Rue"

# ----------------------------------------------------------------
# ✅ ASSIGN NOTE
# ----------------------------------------------------------------
def test_assign_note_to_eleve():
    db = TestingSessionLocal()
    note = Note(titre="Note", contenu="Test", auteur_id=1, equipe="Dev")
    db.add(note)
    db.commit()
    note_id = note.id
    db.close()

    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.put(f"/eleves/{eleve['id']}/assign_note/{note_id}")
    assert r.status_code == 200
    assert r.json()["note_id"] == note_id

# ----------------------------------------------------------------
# ✅ UNASSIGN NOTE
# ----------------------------------------------------------------
def test_unassign_note_from_eleve():
    db = TestingSessionLocal()
    note = Note(titre="Note", contenu="Test", auteur_id=1, equipe="Dev")
    db.add(note)
    db.commit()
    note_id = note.id
    db.close()

    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    client.put(f"/eleves/{eleve['id']}/assign_note/{note_id}")

    r = client.put(f"/eleves/{eleve['id']}/unassign_note")
    assert r.status_code == 200
    assert r.json()["note_id"] is None

# ----------------------------------------------------------------
# ✅ GET HISTORY
# ----------------------------------------------------------------
def test_get_eleve_history():
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()

    # 🟢 Trigger history by updating the student
    client.put(f"/eleves/{eleve['id']}", json={"nom":"A","prenom":"B","adresse":"Rue X"})

    r = client.get(f"/eleves/{eleve['id']}/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


# ----------------------------------------------------------------
# ✅ DELETE ELEVE
# ----------------------------------------------------------------
def test_delete_eleve():
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.delete(f"/eleves/{eleve['id']}")
    assert r.status_code in (200, 204)
