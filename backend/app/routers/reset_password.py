from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.auth import create_reset_token, verify_reset_token, hash_password
from app.emails import send_reset_password_email
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Password Reset"])

# -----------------------------------------------------------
# 📨 1️⃣ Envoi de l'email de réinitialisation
# -----------------------------------------------------------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(Utilisateur).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    token = create_reset_token(user.email)
    background_tasks.add_task(send_reset_password_email, user.email, user.nom, token)

    return {"message": "📧 Email de réinitialisation envoyé avec succès !"}


# -----------------------------------------------------------
# 🔐 2️⃣ Réinitialisation du mot de passe via le lien reçu
# -----------------------------------------------------------
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Lien invalide ou expiré")

    user = db.query(Utilisateur).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.mot_de_passe = hash_password(data.new_password)
    user.is_active = True  # ✅ activation automatique après reset
    db.commit()

    return {"message": "🔐 Mot de passe réinitialisé avec succès ✅"}
