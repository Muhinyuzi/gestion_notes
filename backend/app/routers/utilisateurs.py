# app/routers/utilisateurs.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import UtilisateurCreate, UtilisateurOut, UtilisateurDetailOut, PaginatedUsers
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
@router.post("/", response_model=dict)
def create_user(
    user: UtilisateurCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer un utilisateur (admin uniquement)."""
    new_user = create_user_service(user, db, current_user, background_tasks)
    return {"status": "success", "data": new_user}


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
    """Lister les utilisateurs avec pagination."""
    data = list_users_service(nom, email, equipe, type_, sort, page, limit, db, current_user)
    return {"status": "success", "data": data}


# ---------------- DETAIL ----------------
@router.get("/{user_id}", response_model=dict)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Afficher le détail d’un utilisateur."""
    user = get_user_detail_service(user_id, db, current_user)
    return {"status": "success", "data": user}


# ---------------- UPDATE ----------------
@router.put("/{user_id}", response_model=dict)
def update_user(
    user_id: int,
    updated: UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Mettre à jour un utilisateur."""
    updated_user = update_user_service(user_id, updated, db, current_user)
    return {"status": "success", "data": updated_user}


# ---------------- DELETE ----------------
@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Supprimer un utilisateur."""
    delete_user_service(user_id, db, current_user)
    return {"status": "success", "data": {"message": "Utilisateur supprimé avec succès"}}


# ---------------- UPLOAD AVATAR ----------------
@router.post("/{user_id}/avatar", response_model=dict)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploader un avatar pour un utilisateur."""
    data = await upload_avatar_service(user_id, file, db)
    return {"status": "success", "data": data}


# ---------------- GET AVATAR ----------------
@router.get("/{user_id}/avatar")
async def get_avatar(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un avatar."""
    return await get_avatar_service(user_id, db)
