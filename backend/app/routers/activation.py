# app/routers/activation.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.auth import verify_activation_token, create_activation_token
from app.emails import send_activation_email
from app.schemas.schemas import EmailRequest

router = APIRouter(prefix="/auth", tags=["Activation"])

# ---------------------------------------------------------
# 🔹 ROUTE 1 : Activation via /auth/activate?token=XYZ (frontend)
# 🔹 ROUTE 2 : Activation via /auth/activate/{token} (backend ou test)
# ---------------------------------------------------------
@router.get("/activate")
def activate_account(token: str, db: Session = Depends(get_db)):
    """Activation via /auth/activate?token=XYZ"""
    return _activate_account_logic(token, db)


@router.get("/activate/{token}")
def activate_account_path(token: str, db: Session = Depends(get_db)):
    """Activation via /auth/activate/<token>"""
    return _activate_account_logic(token, db)


# ---------------------------------------------------------
# 🔹 LOGIQUE COMMUNE : Validation + mise à jour du compte
# ---------------------------------------------------------
def _activate_account_logic(token: str, db: Session):
    email = verify_activation_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Lien d’activation invalide ou expiré")

    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # ✅ Support des deux champs possibles : is_active ou actif
    if hasattr(user, "is_active"):
        if user.is_active:
            return {"message": "Compte déjà activé ✅"}
        user.is_active = True
    elif hasattr(user, "actif"):
        if user.actif:
            return {"message": "Compte déjà activé ✅"}
        user.actif = True
    else:
        raise HTTPException(status_code=400, detail="Aucun champ d’activation trouvé sur le modèle utilisateur.")

    db.commit()
    return {"message": "Votre compte a été activé avec succès 🎉"}


# ---------------------------------------------------------
# 🔹 ROUTE : Renvoyer un email d’activation
# ---------------------------------------------------------
@router.post("/resend-activation")
async def resend_activation(request: EmailRequest, db: Session = Depends(get_db)):
    """
    Permet à un utilisateur non activé de redemander son lien d’activation.
    """
    email = request.email

    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Vérifie les deux champs possibles
    is_active = getattr(user, "is_active", getattr(user, "actif", False))
    if is_active:
        return {"message": "Ce compte est déjà activé ✅"}

    token = create_activation_token(email)
    await send_activation_email(email, user.nom, token)

    return {"message": "Email d’activation renvoyé 📩"}
