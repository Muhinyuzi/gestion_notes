from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks 
from fastapi.responses import FileResponse 
import os 
import shutil 
from sqlalchemy.orm import Session, joinedload 
from typing import List 
from app.db import get_db 
from app.emails import send_registration_email
from app.models.utilisateur import Utilisateur 
from app.schemas.schemas import UtilisateurCreate, UtilisateurOut, UtilisateurDetailOut
from passlib.context import CryptContext 
from app.auth import get_current_user
from app.services.utilisateurs import (
    create_user_service,
    list_users_service,
    get_user_detail_service,
    update_user_service,
    delete_user_service,
    upload_avatar_service,
    get_avatar_service,
)

router = APIRouter()

# ---------------- CREATE ----------------
@router.post("/", response_model=UtilisateurOut)
def create_user(
    user: UtilisateurCreate,
    background_tasks: BackgroundTasks,  # ✅ ajout
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    new_user = create_user_service(user, db, current_user)

    # ✅ Envoi email en tâche de fond
    background_tasks.add_task(
        send_registration_email,
        new_user.email,
        new_user.nom
    )

    return new_user

# ---------------- LIST ----------------
@router.get("/", response_model=dict)
def list_users(
    nom: str = Query("", description="Filtrer par nom"),
    email: str = Query("", description="Filtrer par email"),
    equipe: str = Query("", description="Filtrer par équipe"),
    type_: str = Query("", alias="type", description="Filtrer par type"),
    sort: str = Query("nom_asc", description="nom_asc, nom_desc, date_asc, date_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return list_users_service(nom, email, equipe, type_, sort, page, limit, db, current_user)

# ---------------- DETAIL ----------------
@router.get("/{user_id}", response_model=UtilisateurDetailOut)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return get_user_detail_service(user_id, db, current_user)

# ---------------- UPDATE ----------------
@router.put("/{user_id}", response_model=UtilisateurOut)
def update_user(
    user_id: int,
    updated: UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return update_user_service(user_id, updated, db, current_user)

# ---------------- DELETE ----------------
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return delete_user_service(user_id, db, current_user)

# ---------------- UPLOAD AVATAR ----------------
@router.post("/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await upload_avatar_service(user_id, file, db)

# ---------------- GET AVATAR ----------------
@router.get("/{user_id}/avatar")
async def get_avatar(
    user_id: int,
    db: Session = Depends(get_db)
):
    return await get_avatar_service(user_id, db)
