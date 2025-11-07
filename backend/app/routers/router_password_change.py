# app/routers/router_password_change.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.auth import verify_password, hash_password, get_current_user as auth_dep

router = APIRouter(prefix="/auth", tags=["Auth"])


class ChangeOwnPasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


@router.patch("/change-password")
def change_own_password(
    data: ChangeOwnPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(auth_dep),
):
    user = db.query(Utilisateur).filter_by(id=current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if not verify_password(data.old_password, user.mot_de_passe):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent")

    user.mot_de_passe = hash_password(data.new_password)
    db.commit()

    return {"message": "Mot de passe modifié avec succès ✅"}


class AdminChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)


@router.patch("/admin/change-password/{user_id}")
def admin_change_user_password(
    user_id: int,
    data: AdminChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(auth_dep),
):
    if current_user.type.lower() != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    user = db.query(Utilisateur).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.mot_de_passe = hash_password(data.new_password)
    db.commit()

    return {"message": "Mot de passe modifié par admin ✅"}
