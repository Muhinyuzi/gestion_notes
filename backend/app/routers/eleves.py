# app/api/v1/eleves.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import EleveOut, EleveCreate, EleveUpdate
from app.services.eleves import (
    create_eleve_service,
    get_eleve_service,
    list_eleves_service,
    update_eleve_service,
    assign_note_service,
    unassign_note_service,
    delete_eleve_service,
    get_eleve_history_service
)
from app.auth import get_current_user

router = APIRouter()

# 🔹 Créer un élève
@router.post("/", response_model=EleveOut)
def create_eleve(
    eleve_in: EleveCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_eleve_service(eleve_in, current_user, db)

# 🔹 Lire un élève
@router.get("/{eleve_id}", response_model=EleveOut)
def get_eleve(eleve_id: int, db: Session = Depends(get_db)):
    return get_eleve_service(eleve_id, db)

# 🔹 Liste
@router.get("/", response_model=List[EleveOut])
def list_eleves(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return list_eleves_service(skip, limit, db)

# 🔹 Mise à jour
@router.put("/{eleve_id}", response_model=EleveOut)
def update_eleve(eleve_id: int, eleve_data: EleveUpdate, db: Session = Depends(get_db)):
    return update_eleve_service(eleve_id, eleve_data, db)

# 🔹 Assigner une note
@router.put("/{eleve_id}/assign_note/{note_id}", response_model=EleveOut)
def assign_note_to_eleve(
    eleve_id: int,
    note_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return assign_note_service(eleve_id, note_id, current_user, db)

# 🔹 Désassigner une note
@router.put("/{eleve_id}/unassign_note", response_model=EleveOut)
def unassign_note_from_eleve(
    eleve_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return unassign_note_service(eleve_id, current_user, db)

# 🔹 Supprimer
@router.delete("/{eleve_id}")
def delete_eleve(
    eleve_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_eleve_service(eleve_id, current_user, db)

# 🔹 Historique
@router.get("/{eleve_id}/history", response_model=List[dict])
def get_eleve_history(eleve_id: int, db: Session = Depends(get_db)):
    return get_eleve_history_service(eleve_id, db)
