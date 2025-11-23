#test_auth.py
from app.config import settings
from jose import jwt

def test_login(client):    
    # Create user (non activé par défaut)
    res = client.post("/utilisateurs/", json={
        "nom": "Bob",
        "email": "bob@test.com",
        "mot_de_passe": "pass",
        "type": "user",
        "equipe": "Dev"
    })
    assert res.status_code == 200
    user = res.json()
    user = user.get("data", user)
    assert user["is_active"] is False

    # Tentative de login → doit échouer (compte non activé)
    response = client.post("/login", data={
        "username": "bob@test.com",
        "password": "pass"
    })
    assert response.status_code == 403  # ✅ 403 maintenant
    assert "pas encore activé" in response.text

    # ✅ Activer manuellement pour le test
    token = jwt.encode(
        {"sub": user["email"], "type": "activation"},
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    client.get(f"/auth/activate?token={token}")

    # Essayer après activation → doit réussir
    response = client.post("/login", data={
        "username": "bob@test.com",
        "password": "pass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    r = client.post("/login", data={"username": "admin@test.com", "password": "wrong"})
    assert r.status_code == 401
