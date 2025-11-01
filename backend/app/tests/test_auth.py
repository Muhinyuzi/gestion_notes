def test_login(client):
    # Create user
    client.post("/utilisateurs/", json={
        "nom": "Bob",
        "email": "bob@test.com",
        "mot_de_passe": "pass",
        "type": "user",
        "equipe": "Dev"
    })

    # Try login
    response = client.post("/login", data={
        "username": "bob@test.com",
        "password": "pass"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
