# app/tests/test_router_utilisateurs.py
import pytest

def test_create_user_router(client):
    data = {
        "nom": "TestUser",
        "email": "router@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200
    res = r.json()
    assert res["email"] == "router@test.com"


def test_list_users_router(client):
    client.post("/utilisateurs/", json={
        "nom": "UserA",
        "email": "usera@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })

    r = client.get("/utilisateurs/")
    assert r.status_code == 200

    data = r.json()
    assert "users" in data
    assert len(data["users"]) == 1


def test_get_user_detail_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserB",
        "email": "userb@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "userb@test.com"


def test_update_user_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserC",
        "email": "userc@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.put(f"/utilisateurs/{user_id}", json={
        "nom": "UpdatedUser",
        "email": "userc@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })

    assert r.status_code == 200
    assert r.json()["nom"] == "UpdatedUser"


def test_delete_user_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserD",
        "email": "userd@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["id"]

    r = client.delete(f"/utilisateurs/{user_id}")
    assert r.status_code == 204

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 404

# Duplicate email
def test_create_user_email_duplicate(client):
    data1 = {
        "nom": "User1",
        "email": "dup@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }

    data2 = {
        "nom": "User2",  # 🔥 Change name to avoid unique name violation
        "email": "dup@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    }

    client.post("/utilisateurs/", json=data1)
    r = client.post("/utilisateurs/", json=data2)

    assert r.status_code == 400
    assert "Email déjà utilisé" in r.text

# Get user not found
def test_get_user_not_found(client):
    r = client.get("/utilisateurs/9999")
    assert r.status_code == 404