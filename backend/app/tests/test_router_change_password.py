# app/tests/test_router_change_password.py

import pytest
from app.tests.conftest import activate_user_via_token


# ==========================================================
# 🔹 TESTS DU CHANGEMENT DE MOT DE PASSE
# ==========================================================

def test_user_change_password_success(user_client, create_test_user_non_admin):
    """✅ Utilisateur normal — changement de mot de passe réussi"""
    email = create_test_user_non_admin["email"]
    old_pass, new_pass = "12345678", "newpass123"

    # 🟢 Activation du compte avant test
    activate_user_via_token(user_client, email)

    # 🔑 Connexion initiale
    login = user_client.post("/login", data={"username": email, "password": old_pass})
    assert login.status_code == 200, f"Échec login: {login.text}"
    token = login.json()["access_token"]

    # 🔐 Changement de mot de passe
    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": old_pass, "new_password": new_pass},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, f"Échec changement mot de passe: {r.text}"
    assert "succès" in r.json()["message"]


def test_admin_change_password_without_old(admin_client, create_test_user):
    """✅ Admin peut changer son mot de passe sans fournir l'ancien"""
    email = create_test_user["email"]
    activate_user_via_token(admin_client, email)

    # 🔑 Connexion initiale
    login = admin_client.post("/login", data={"username": email, "password": "12345678"})
    assert login.status_code == 200, f"Échec login admin: {login.text}"
    token = login.json()["access_token"]

    # 🔐 Changement sans ancien mot de passe
    r = admin_client.patch(
        "/auth/change-password",
        json={"new_password": "supersecret"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, f"Échec changement admin: {r.text}"
    assert "succès" in r.json()["message"]


def test_change_password_wrong_old_password(user_client, create_test_user_non_admin):
    """🚫 Ancien mot de passe incorrect"""
    email = create_test_user_non_admin["email"]
    activate_user_via_token(user_client, email)

    # 🔑 Connexion initiale
    login = user_client.post("/login", data={"username": email, "password": "12345678"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    # 🚫 Ancien mot de passe erroné
    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": "wrongpass", "new_password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400, f"Code attendu 400, reçu {r.status_code}: {r.text}"
    assert "incorrect" in r.json()["detail"]


def test_change_password_same_as_old(user_client, create_test_user_non_admin):
    """🚫 Ancien mot de passe = nouveau → rejeté"""
    email = create_test_user_non_admin["email"]
    activate_user_via_token(user_client, email)

    # 🔑 Connexion initiale
    login = user_client.post("/login", data={"username": email, "password": "12345678"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    # 🚫 Ancien = nouveau
    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": "12345678", "new_password": "12345678"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400, f"Réponse inattendue: {r.text}"
    assert "différent" in r.json()["detail"]
