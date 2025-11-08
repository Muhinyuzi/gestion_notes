# =====================================================
# app/emails.py – version sécurisée pour tests/CI/CD
# Empêche tout envoi SMTP réel pendant les tests.
# =====================================================

import os
from datetime import datetime
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings

# 🧩 Force le mode test dès le chargement du module (important)
os.environ.setdefault("TESTING", "1")

# ✅ Détection automatique du mode test / CI
IS_TESTING = (
    os.getenv("TESTING") == "1"
    or os.getenv("PYTEST_CURRENT_TEST") is not None
    or os.getenv("CI") == "true"
)

# ✅ Configuration de connexion (utilisée uniquement hors test)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER="app/templates/emails"
)


# -------------------------------------------------------
# 🧩 Helper : Envoi sécurisé (désactivé pendant les tests)
# -------------------------------------------------------
async def _safe_send_email(message: MessageSchema, template_name: str):
    print(f"📨 _safe_send_email appelé → {message.subject} ({message.recipients})")
    """Empêche tout envoi SMTP réel en mode test ou CI/CD."""
    if IS_TESTING:
        log_line = f"[TEST MODE] Email simulé → {message.recipients[0]} | Sujet: {message.subject}"
        print(log_line)

        # Sauvegarde optionnelle dans un log local
        log_path = "app/logs/test_emails.log"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        return
    print(f"🚀 Envoi réel d’un email à {message.recipients} via {conf.MAIL_SERVER}:{conf.MAIL_PORT}")
    fm = FastMail(conf)
    await fm.send_message(message, template_name=template_name)


# -------------------------------------------------------
# 📨 Email de bienvenue
# -------------------------------------------------------
async def send_registration_email(to_email: str, user_name: str, plain_password: str):
    message = MessageSchema(
        subject="🎉 Bienvenue sur Gestion Notes",
        recipients=[to_email],
        template_body={
            "name": user_name,
            "password": plain_password,
            "year": datetime.now().year
        },
        subtype="html"
    )
    await _safe_send_email(message, "welcome.html")


# -------------------------------------------------------
# 📨 Email d’activation
# -------------------------------------------------------
async def send_activation_email(to_email: str, user_name: str, token: str):
    activation_link = f"http://localhost:4200/activate?token={token}"
    message = MessageSchema(
        subject="🔓 Activez votre compte - Gestion Notes",
        recipients=[to_email],
        template_body={
            "name": user_name,
            "activation_link": activation_link,
            "year": datetime.now().year
        },
        subtype="html"
    )
    await _safe_send_email(message, "activation.html")


# -------------------------------------------------------
# 📨 Email de réinitialisation de mot de passe
# -------------------------------------------------------
async def send_reset_password_email(to_email: str, user_name: str, token: str):
    reset_link = f"http://localhost:4200/reset-password?token={token}"
    message = MessageSchema(
        subject="🔐 Réinitialisation de votre mot de passe - Gestion Notes",
        recipients=[to_email],
        template_body={
            "name": user_name,
            "reset_link": reset_link,
            "year": datetime.now().year
        },
        subtype="html"
    )
    await _safe_send_email(message, "reset_password.html")
