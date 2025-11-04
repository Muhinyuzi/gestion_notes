# app/tests/test_router_eleves.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import TestingSessionLocal
from app.models.note import Note

client = TestClient(app)

def test_create_eleve(create_test_user):
    r = client.post("/eleves/", json={"nom":"Jean","prenom":"Claude"})
    assert r.status_code == 200
    assert r.json()["nom"] == "Jean"


def test_get_eleve(create_test_user):
    res = client.post("/eleves/", json={"nom":"A","prenom":"B"})
    eleve_id = res.json()["id"]

    r = client.get(f"/eleves/{eleve_id}")
    assert r.status_code == 200
    assert r.json()["id"] == eleve_id


def test_list_eleves(client, create_test_user):
    r0 = client.get("/eleves/")
    initial = len(r0.json())

    client.post("/eleves/", json={"nom":"A","prenom":"B"})
    r = client.get("/eleves/")

    assert r.status_code == 200
    assert len(r.json()) == initial + 1


def test_update_eleve(create_test_user):
    res = client.post("/eleves/", json={"nom":"A","prenom":"B"})
    eleve_id = res.json()["id"]

    r = client.put(
        f"/eleves/{eleve_id}",
        json={"nom":"A","prenom":"B","adresse":"Rue X","updated_by":create_test_user["id"]}
    )
    assert r.status_code == 200
    assert r.json()["adresse"] == "Rue X"


def test_assign_note_to_eleve(create_test_user):
    db = TestingSessionLocal()
    note = Note(titre="N", contenu="T", auteur_id=create_test_user["id"], equipe="Dev")
    db.add(note); db.commit()
    note_id = note.id
    db.close()

    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.put(f"/eleves/{eleve['id']}/assign_note/{note_id}")

    assert r.status_code == 200
    assert r.json()["note_id"] == note_id


def test_unassign_note_from_eleve(create_test_user):
    db = TestingSessionLocal()
    note = Note(titre="N", contenu="T", auteur_id=create_test_user["id"], equipe="Dev")
    db.add(note); db.commit()
    note_id = note.id
    db.close()

    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    client.put(f"/eleves/{eleve['id']}/assign_note/{note_id}")

    r = client.put(f"/eleves/{eleve['id']}/unassign_note")
    assert r.status_code == 200
    assert r.json()["note_id"] is None


def test_get_eleve_history(create_test_user):
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()

    client.put(
        f"/eleves/{eleve['id']}",
        json={"nom":"A","prenom":"B","adresse":"Rue","updated_by":create_test_user["id"]}
    )

    r = client.get(f"/eleves/{eleve['id']}/history")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_delete_eleve(create_test_user):
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.delete(f"/eleves/{eleve['id']}")
    assert r.status_code in (200,204)


# --- ERROR CASES ---

def test_assign_note_eleve_not_found(client):
    r = client.put("/eleves/999/assign_note/1")
    assert r.status_code == 404

def test_assign_note_not_found(client):
    eleve = client.post("/eleves/", json={"nom": "A", "prenom": "B"}).json()
    r = client.put(f"/eleves/{eleve['id']}/assign_note/999")
    assert r.status_code == 404

def test_unassign_note_none(client):
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.put(f"/eleves/{eleve['id']}/unassign_note")
    assert r.status_code == 400

def test_get_eleve_not_found(client):
    r = client.get("/eleves/999")
    assert r.status_code == 404

def test_update_eleve_not_found(client):
    r = client.put("/eleves/999", json={"nom":"A","prenom":"B","adresse":"Rue","updated_by":1})
    assert r.status_code == 404

def test_delete_eleve_not_found(client):
    r = client.delete("/eleves/999")
    assert r.status_code == 404

def test_get_eleve_history_not_found(client):
    r = client.get("/eleves/999/history")
    assert r.status_code == 404

def test_create_eleve_missing_fields(client):
    r = client.post("/eleves/", json={"prenom":"Claude"})
    assert r.status_code == 422

def test_update_eleve_missing_updated_by(client):
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.put(f"/eleves/{eleve['id']}", json={"nom":"A","prenom":"B","adresse":"Rue X"})
    assert r.status_code == 422

def test_update_eleve_no_changes(client, create_test_user):
    eleve = client.post("/eleves/", json={"nom":"A","prenom":"B"}).json()
    r = client.put(
        f"/eleves/{eleve['id']}",
        json={"nom":"A","prenom":"B","updated_by":create_test_user["id"]}
    )
    assert r.status_code == 400    