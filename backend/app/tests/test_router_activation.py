# app/tests/test_router_activation.py
import pytest
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

def test_user_activation(client):
    """Test complet du flux d’activation de compte"""

    # 1️⃣ Création utilisateur inactif
    data = {
        "nom": "UserActivation",
        "email": "activation@test.com",
        "mot_de_passe": "12345678",
        "type": "admin",
        "equipe": "Dev"
    }
    r = client.post("/utilisateurs/", json=data)
    assert r.status_code == 200
    #user = r.json()
    data = r.json().get("data", r.json())
    assert not data["is_active"]

    # 2️⃣ Générer un token valide
    token = jwt.encode(
        {
            "sub": data["email"],
            "type": "activation",
            "exp": datetime.utcnow() + timedelta(hours=24)
        },
        settings.JWT_SECRET,
        algorithm="HS256"
    )

    # 3️⃣ Activer le compte
    r = client.get(f"/auth/activate/{token}")
    assert r.status_code == 200
    assert "activé" in r.json()["message"]

    # 4️⃣ Vérifier que le user est actif
    r = client.get(f"/utilisateurs/{data['id']}")
    assert r.status_code == 200

    res = r.json()
    user_data = res.get("data", res)
    assert user_data["is_active"] is True

    # 5️⃣ Connexion après activation
    login_data = {"username": data["email"], "password": "12345678"}
    r = client.post("/login", data=login_data)
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_resend_activation_email(client, create_test_user):
    """Test du renvoi d’email d’activation"""
    email = create_test_user["email"]

    r = client.post("/auth/resend-activation", json={"email": email})
    assert r.status_code == 200
    assert "renvoyé" in r.text.lower()
