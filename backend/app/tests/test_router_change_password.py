# app/tests/test_router_change_password.py
import pytest
from app.tests.conftest import activate_user_via_token


def test_user_change_password_success(user_client, create_test_user_non_admin):
    """✅ Utilisateur normal change SON mot de passe."""

    email = create_test_user_non_admin["email"]
    old_pass = "12345678"
    new_pass = "newpass123"

    # ✅ Activation obligatoire
    activate_user_via_token(user_client, email)

    # ✅ Login utilisateur
    login = user_client.post("/login", data={"username": email, "password": old_pass})
    assert login.status_code == 200
    token = login.json()["access_token"]

    # ✅ Changement du mot de passe
    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": old_pass, "new_password": new_pass},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert "modifié" in r.json()["message"]

    # ✅ Vérifier connexion avec le nouveau mot de passe
    login2 = user_client.post("/login", data={"username": email, "password": new_pass})
    assert login2.status_code == 200


def test_change_password_wrong_old_password(user_client, create_test_user_non_admin):
    """🚫 Ancien mot de passe incorrect."""

    email = create_test_user_non_admin["email"]

    activate_user_via_token(user_client, email)
    login = user_client.post("/login", data={"username": email, "password": "12345678"})
    token = login.json()["access_token"]

    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": "WRONGPASS", "new_password": "new123456"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 400
    assert "incorrect" in r.json()["detail"]


def test_change_password_same_as_old(user_client, create_test_user_non_admin):
    """🚫 Impossible d'utiliser le même mot de passe."""

    email = create_test_user_non_admin["email"]

    activate_user_via_token(user_client, email)
    login = user_client.post("/login", data={"username": email, "password": "12345678"})
    token = login.json()["access_token"]

    r = user_client.patch(
        "/auth/change-password",
        json={"old_password": "12345678", "new_password": "12345678"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 400
    assert "différent" in r.json()["detail"]


def test_admin_change_password_of_other_user(admin_client, create_test_user, create_test_user_non_admin):
    """✅ Admin modifie le mot de passe d'un autre utilisateur."""

    admin_email = create_test_user["email"]
    target_email = create_test_user_non_admin["email"]
    target_id = create_test_user_non_admin["id"]

    # ✅ activer comptes
    activate_user_via_token(admin_client, admin_email)
    activate_user_via_token(admin_client, target_email)

    # ✅ login admin
    login = admin_client.post("/login", data={"username": admin_email, "password": "12345678"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    # ✅ changement mot de passe
    r = admin_client.patch(
        f"/auth/admin/change-password/{target_id}",
        json={"new_password": "changedByAdmin!"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    assert "modifié" in r.json()["message"]

    # ✅ vérifier login du target
    login2 = admin_client.post(
        "/login", data={"username": target_email, "password": "changedByAdmin!"}
    )
    assert login2.status_code == 200


def test_non_admin_cannot_change_other_user_password(user_client, create_test_user_non_admin):

    user = create_test_user_non_admin
    activate_user_via_token(user_client, user["email"])

    login = user_client.post("/login", data={"username": user["email"], "password": "12345678"})
    token = login.json()["access_token"]

    r = user_client.patch(
        "/auth/admin/change-password/999",
        json={"new_password": "whatever"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 403
    assert r.json()["detail"] == "Accès réservé aux administrateurs"
