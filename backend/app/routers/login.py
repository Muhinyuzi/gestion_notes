from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.utilisateur import Utilisateur
import app.auth  # contient create_access_token et verify_password

router = APIRouter(tags=["auth"])  # pas de prefix pour garder /login

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Cherche l'utilisateur par email
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user or not app.auth.verify_password(form_data.password, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
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
