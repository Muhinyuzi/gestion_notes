# app/tests/test_router_utilisateurs.py
import pytest

def test_create_user_router(client):
    data = {
        "nom": "TestUser",
        "email": "router@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200

    res = r.json()
    assert res["status"] == "success"
    assert res["data"]["email"] == "router@test.com"
    assert res["data"]["is_active"] is False


def test_list_users_router(client):
    client.post("/utilisateurs/", json={
        "nom": "UserA",
        "email": "usera@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })

    r = client.get("/utilisateurs/")
    assert r.status_code == 200

    data = r.json()["data"]
    assert "users" in data
    assert any(u["email"] == "usera@test.com" for u in data["users"])


def test_get_user_detail_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserB",
        "email": "userb@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["data"]["id"]

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 200
    assert r.json()["data"]["email"] == "userb@test.com"


def test_update_user_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserC",
        "email": "userc@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["data"]["id"]

    r = client.put(f"/utilisateurs/{user_id}", json={
        "nom": "UpdatedUser",
        "email": "userc@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })

    assert r.status_code == 200
    assert r.json()["data"]["nom"] == "UpdatedUser"


def test_delete_user_router(client):
    r = client.post("/utilisateurs/", json={
        "nom": "UserD",
        "email": "userd@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    })
    user_id = r.json()["data"]["id"]

    r = client.delete(f"/utilisateurs/{user_id}")
    assert r.status_code == 200  # maintenant 200 (plus 204)
    assert r.json()["status"] == "success"
    assert "message" in r.json()["data"]

    r = client.get(f"/utilisateurs/{user_id}")
    assert r.status_code == 404


def test_create_user_email_duplicate(client):
    data1 = {
        "nom": "User1",
        "email": "dup@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    }

    data2 = {
        "nom": "User2",
        "email": "dup@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    }

    client.post("/utilisateurs/", json=data1)
    r = client.post("/utilisateurs/", json=data2)

    assert r.status_code == 400
    assert "Un utilisateur avec cet email existe déjà." in r.text


def test_get_user_not_found(client):
    r = client.get("/utilisateurs/9999")
    assert r.status_code == 404
