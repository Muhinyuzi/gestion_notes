from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS= False,  # ex-TLS
    MAIL_SSL_TLS=True, 
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER="app/templates/emails"
)

async def send_registration_email(to_email: str, user_name: str):
    message = MessageSchema(
        subject="✅ Votre compte a été créé - Gestion Notes",
        recipients=[to_email],
        template_body={"name": user_name},
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="welcome.html")