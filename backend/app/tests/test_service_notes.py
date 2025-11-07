# app/tests/test_router_notes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import TestingSessionLocal, debug_dump_db, current_test_user

client = TestClient(app)

# -----------------------------------------------------------------
# ✅ TEST CREATE NOTE
# -----------------------------------------------------------------
def test_create_note_router(create_test_user):
    data = {
        "titre": "Note Test",
        "contenu": "Contenu Test",
        "auteur_id": create_test_user["id"],
        "equipe": "Dev",
        "priorite": "haute",
        "categorie": "info"
    }
    r = client.post("/notes/", json=data)
    assert r.status_code == 200
    assert r.json()["titre"] == "Note Test"


# -----------------------------------------------------------------
# ✅ TEST LIST NOTES
# -----------------------------------------------------------------
def test_list_notes_router(client, create_test_user):
    # total initial
    r0 = client.get("/notes/")
    initial_total = r0.json()["total"]

    payload = {
        "titre": "Note test",
        "contenu": "Contenu",
        "auteur_id": create_test_user["id"]
    }

    client.post("/notes/", json=payload)

    r = client.get("/notes/")
    assert r.status_code == 200
    assert r.json()["total"] == initial_total + 1


# -----------------------------------------------------------------
# ✅ TEST DETAIL
# -----------------------------------------------------------------
def test_get_note_detail_router(create_test_user):
    create = client.post("/notes/", json={"titre":"A","contenu":"B", "auteur_id": create_test_user["id"]})
    note_id = create.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["id"] == note_id


# -----------------------------------------------------------------
# ✅ TEST LIKE NOTE
# -----------------------------------------------------------------
def test_like_note_router(create_test_user):
    create = client.post("/notes/", json={"titre":"L","contenu":"c","auteur_id":create_test_user["id"]})
    note_id = create.json()["id"]

    r = client.post(f"/notes/{note_id}/like")
    assert r.status_code == 200
    assert r.json()["likes"] == 1


# -----------------------------------------------------------------
# ✅ TEST COMMENTS
# -----------------------------------------------------------------
def test_add_commentaire_router(create_test_user):
    create = client.post("/notes/", json={"titre":"C","contenu":"text","auteur_id":create_test_user["id"]})
    note_id = create.json()["id"]

    commentaire = {"contenu":"Salut","auteur_id":create_test_user["id"]}
    r = client.post(f"/notes/{note_id}/commentaires", json=commentaire)

    assert r.status_code == 200
    assert r.json()["contenu"] == "Salut"


def test_get_commentaires_router(create_test_user):
    create = client.post("/notes/", json={"titre":"C","contenu":"text","auteur_id":create_test_user["id"]})
    note_id = create.json()["id"]

    client.post(f"/notes/{note_id}/commentaires",
                json={"contenu":"Test","auteur_id":create_test_user["id"]})

    r = client.get(f"/notes/{note_id}/commentaires")
    assert r.status_code == 200
    assert len(r.json()) == 1


# -----------------------------------------------------------------
# ✅ TEST DELETE NOTE
# -----------------------------------------------------------------
def test_delete_note_router(create_test_user):
    create = client.post("/notes/", json={"titre":"D","contenu":"z","auteur_id":create_test_user["id"]})
    note_id = create.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code in (200, 204)

def test_create_note_missing_title(client, create_test_user):
    payload = {
        "contenu": "Test no title",
        "auteur_id": create_test_user["id"]
    }
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422

def test_get_note_not_found(client):
    r = client.get("/notes/999")
    assert r.status_code == 404

