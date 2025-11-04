# app/tests/test_router_commentaires.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_commentaire_router_success(client, create_test_user):
    # Create note
    note = client.post("/notes/", json={"titre":"T","contenu":"C","auteur_id":create_test_user["id"]}).json()
    note_id = note["id"]

    r = client.post(f"/notes/{note_id}/commentaires",
                    json={"contenu":"Hello","auteur_id":create_test_user["id"]})

    assert r.status_code == 200
    assert r.json()["contenu"] == "Hello"


def test_add_commentaire_router_note_not_found():
    r = client.post("/notes/999/commentaires", json={"contenu":"Hello","auteur_id":1})
    assert r.status_code == 404


def test_add_commentaire_router_author_not_found(client, create_test_user):
    note = client.post("/notes/", json={"titre":"T","contenu":"C","auteur_id":create_test_user["id"]}).json()
    note_id = note["id"]

    r = client.post(f"/notes/{note_id}/commentaires", json={"contenu":"Hello","auteur_id":999})
    assert r.status_code == 404
