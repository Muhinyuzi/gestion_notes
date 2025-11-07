from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.utilisateur import Utilisateur
import app.auth

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # 🔹 Si JSON: on parse manuellement
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
        username = data.get("email")
        password = data.get("password")
    else:
        # 🔹 Si formulaire OAuth2
        username = form_data.username
        password = form_data.password

    user = db.query(Utilisateur).filter(Utilisateur.email == username).first()

    if not user or not app.auth.verify_password(password, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Vérifier activation
    if not user.is_active:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Votre compte n’est pas encore activé. Vérifiez vos emails."
    )

    token = app.auth.create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "equipe": user.equipe,
            "type": user.type
        }
    }
