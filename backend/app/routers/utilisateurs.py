from fastapi import (
    APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
)
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import UtilisateurCreate, UtilisateurOut, UtilisateurDetailOut
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✅ Crée un nouvel utilisateur et renvoie directement l'objet créé
    (compatible avec les anciens tests et le frontend).
    """
    new_user = create_user_service(user, db, current_user, background_tasks)
    return new_user


# ---------------- LIST ----------------
@router.get("/", response_model=List[UtilisateurOut])
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
    """
    ✅ Renvoie directement une liste d'utilisateurs.
    (plus de structure {'status':..., 'data':...})
    """
    return list_users_service(nom, email, equipe, type_, sort, page, limit, db, current_user)


# ---------------- DETAIL ----------------
@router.get("/{user_id}", response_model=UtilisateurDetailOut)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✅ Détails d'un utilisateur spécifique.
    """
    return get_user_detail_service(user_id, db, current_user)


# ---------------- UPDATE ----------------
@router.put("/{user_id}", response_model=UtilisateurOut)
def update_user(
    user_id: int,
    updated: UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✅ Met à jour un utilisateur et renvoie l'objet mis à jour.
    """
    return update_user_service(user_id, updated, db, current_user)


# ---------------- DELETE ----------------
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ✅ Supprime un utilisateur.
    """
    delete_user_service(user_id, db, current_user)
    return None  # 204 = pas de contenu à retourner


# ---------------- UPLOAD AVATAR ----------------
@router.post("/{user_id}/avatar", response_model=UtilisateurOut)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    ✅ Upload de l'avatar avec vérification de taille et type.
    """
    # Limite de taille : 2 Mo
    MAX_SIZE = 2 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 2 Mo)")

    # Type MIME accepté
    if not file.content_type.startswith(("image/jpeg", "image/png", "image/jpg")):
        raise HTTPException(status_code=400, detail="Format de fichier non supporté (jpg, jpeg, png uniquement)")

    # On réécrit le flux pour la sauvegarde après lecture
    from io import BytesIO
    file.file = BytesIO(content)

    updated_user = await upload_avatar_service(user_id, file, db)
    return updated_user


# ---------------- GET AVATAR ----------------
@router.get("/{user_id}/avatar")
async def get_avatar(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    ✅ Récupère le fichier avatar d'un utilisateur.
    """
    return await get_avatar_service(user_id, db)

