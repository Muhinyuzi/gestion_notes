from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, StringConstraints
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.auth import verify_password, hash_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class ChangePasswordRequest(BaseModel):
    old_password: str | None = None
    new_password: Annotated[str, StringConstraints(min_length=8)]


@router.patch("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: dict | Utilisateur = Depends(get_current_user),  # 🔥 accepte dict OU ORM
):
    """
    🔐 Permet à l'utilisateur connecté (admin ou non) de changer son mot de passe.
    - Admin → pas besoin de fournir l'ancien mot de passe.
    - Utilisateur normal → doit fournir l'ancien mot de passe valide.
    """

    # ✅ Récupération universelle de l'ID ou email
    user_id = getattr(current_user, "id", None) or current_user.get("id")
    email = getattr(current_user, "email", None) or current_user.get("email")

    # 🔍 Recherche de l'utilisateur en DB (par ID ou email)
    user = db.query(Utilisateur).filter(
        (Utilisateur.id == user_id) | (Utilisateur.email == email)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # ✅ Déterminer le type d'utilisateur (admin ou non)
    user_type = (getattr(user, "type", "") or "").lower()

    # 🔒 Vérifications pour utilisateurs non-admin
    if user_type != "admin":
        if not data.old_password:
            raise HTTPException(status_code=400, detail="Ancien mot de passe requis")

        if not verify_password(data.old_password, user.mot_de_passe):
            raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

        if data.old_password == data.new_password:
            raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")

    # ✅ Mise à jour du mot de passe
    user.mot_de_passe = hash_password(data.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Mot de passe mis à jour avec succès ✅",
        "user": {"id": user.id, "email": user.email, "type": user.type},
    }
