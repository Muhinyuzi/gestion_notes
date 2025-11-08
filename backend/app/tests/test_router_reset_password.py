from jose import jwt
from app.config import settings

def test_forgot_and_reset_password(client, create_test_user):
    """Test complet du flux de réinitialisation du mot de passe"""

    # --- 1️⃣ Envoi du lien de réinitialisation ---
    email = create_test_user["email"]
    r = client.post("/auth/forgot-password", json={"email": email})
    assert r.status_code == 200, r.text
    assert "Email de réinitialisation" in r.json()["message"]

    # --- 2️⃣ Création d’un token valide ---
    token = jwt.encode(
        {"sub": email, "type": "reset"},
        settings.JWT_SECRET,
        algorithm="HS256"
    )

    # --- 3️⃣ Réinitialisation du mot de passe ---
    new_password = "newpassword123"
    r2 = client.post("/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })
    assert r2.status_code == 200, r2.text
    assert "réinitialisé" in r2.json()["message"]

    # --- 4️⃣ Activer l'utilisateur pour tester le login ---
    activation_token = jwt.encode(
        {"sub": email, "type": "activation"},
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    activate = client.get(f"/auth/activate?token={activation_token}")
    assert activate.status_code == 200, activate.text

    # --- 5️⃣ Tentative de connexion avec le nouveau mot de passe ---
    login = client.post("/login", data={
        "username": email,
        "password": new_password
    })
    assert login.status_code == 200, login.text
    assert "access_token" in login.json()


def test_forgot_password_user_not_found(client):
    """Test erreur si l’email n’existe pas"""
    r = client.post("/auth/forgot-password", json={"email": "nope@test.com"})
    assert r.status_code == 404
    assert "introuvable" in r.text.lower()


def test_reset_password_invalid_token(client):
    """Test avec token invalide"""
    r = client.post("/auth/reset-password", json={
        "token": "invalidtoken",
        "new_password": "test123"
    })
    assert r.status_code == 400
    assert "invalide" in r.text.lower()
