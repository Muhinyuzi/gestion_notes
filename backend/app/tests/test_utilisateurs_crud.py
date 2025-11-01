def test_list_users(client, create_test_user):
    r = client.get("/utilisateurs/")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, dict)  # la réponse est un dict
    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) >= 1


def test_get_user_by_id(client, create_test_user):
    user = create_test_user
    r = client.get(f"/utilisateurs/{user['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == user["id"]


def test_update_user(client, create_test_user):
    user = create_test_user
    r = client.put(f"/utilisateurs/{user['id']}", json={
        "nom": "Updated Name",
        "email": f"updated_{user['email']}",
        "mot_de_passe": "newpass",
        "type": "admin",
        "equipe": "TestTeam"
    })
    assert r.status_code == 200
    assert r.json()["nom"] == "Updated Name"


def test_delete_user(client, create_test_user):
    user = create_test_user
    r = client.delete(f"/utilisateurs/{user['id']}")
    assert r.status_code in (200, 204)

    r2 = client.get(f"/utilisateurs/{user['id']}")
    assert r2.status_code == 404
