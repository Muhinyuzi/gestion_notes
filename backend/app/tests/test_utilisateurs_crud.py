# app/tests/test_utilisateurs_crud.py
import pytest

def test_list_users(client):
    client.post("/utilisateurs/", json={
        "nom": "UserA",
        "email": "usera_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })

    r = client.get("/utilisateurs/")
    assert r.status_code == 200
    data = r.json()

    assert "users" in data
    assert any(u["email"] == "usera_crud@test.com" for u in data["users"])


def test_get_user_by_id(client):
    # Création
    r = client.post("/utilisateurs/", json={
        "nom": "UserB",
        "email": "userb_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    assert r.status_code == 200
    user_id = r.json()["id"]

    # Lecture
    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "userb_crud@test.com"


def test_update_user(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserC",
        "email": "userc_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.put(f"/utilisateurs/{user_id}", json={
        "nom": "UpdatedC",
        "email": "userc_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })

    assert r.status_code == 200
    assert r.json()["nom"] == "UpdatedC"


def test_delete_user(client):
    # 🔹 Création
    r = client.post("/utilisateurs/", json={
        "nom": "UserD",
        "email": "userd_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    # 🔹 Suppression
    r = client.delete(f"/utilisateurs/{user_id}")
    assert r.status_code in (200, 204)

    # 🔹 Vérifie que l’utilisateur est bien supprimé
    r2 = client.get(f"/utilisateurs/{user_id}")
    assert r2.status_code == 404


def test_create_duplicate_email(client):
    data = {
        "nom": "UserE",
        "email": "dup_crud@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    }

    client.post("/utilisateurs/", json=data)
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 400
    assert "Un utilisateur avec cet email existe déjà." in r.text


def test_get_user_not_found(client):
    r = client.get("/utilisateurs/9999")
    assert r.status_code == 404
    assert "Utilisateur non trouvé" in r.text
