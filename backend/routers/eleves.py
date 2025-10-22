from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from db import get_db
from models import Eleve, EleveHistory, Utilisateur, log_eleve_change
from schemas import EleveOut, EleveCreate, EleveUpdate
from auth import get_current_user

router = APIRouter()

# 🔹 Créer un élève
@router.post("/", response_model=EleveOut)
def create_eleve(
    eleve_in: EleveCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    eleve = Eleve(
        **eleve_in.dict(),
        created_by=current_user.id
    )
    db.add(eleve)
    db.commit()
    db.refresh(eleve)
    return eleve

# 🔹 Lire un élève par ID
@router.get("/{eleve_id}", response_model=EleveOut)
def get_eleve(
    eleve_id: int,
    db: Session = Depends(get_db)
):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    return eleve

# 🔹 Liste de tous les élèves
@router.get("/", response_model=List[EleveOut])
def list_eleves(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return db.query(Eleve).offset(skip).limit(limit).all()

# 🔹 Mettre à jour un élève (inclus historique)
@router.put("/{eleve_id}", response_model=EleveOut)
def update_eleve(eleve_id: int, eleve_data: EleveUpdate, db: Session = Depends(get_db)):
    # 1️⃣ Récupérer l'élève
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    # 2️⃣ Calculer les changements pour log
    changes = {}
    for field, new_value in eleve_data.dict(exclude_unset=True).items():
        old_value = getattr(eleve, field)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
            setattr(eleve, field, new_value)  # Met à jour l'élève

    if changes:
        # Mettre à jour la date de modification
        eleve.updated_at = datetime.utcnow()

        # 3️⃣ Enregistrer les changements dans l'historique
        log_eleve_change(
            session=db,
            eleve_id=eleve.id,
            user_id=eleve_data.updated_by,
            changes=changes,
            raison_changement="Mise à jour depuis l'API"  # tu peux personnaliser
        )

    db.commit()
    db.refresh(eleve)
    return eleve

# 🔹 Assigner une note à un élève
@router.put("/{eleve_id}/assign_note/{note_id}", response_model=EleveOut)
def assign_note_to_eleve(
    eleve_id: int,
    note_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    old_note_id = eleve.note_id
    eleve.note_id = note_id
    eleve.date_note_assignee = datetime.utcnow()
    eleve.updated_by = current_user.id
    db.add(eleve)

    # Historique
    history = EleveHistory(
        eleve_id=eleve.id,
        edited_by=current_user.id,
        edited_at=datetime.utcnow(),
        changes={"note_id": {"old": old_note_id, "new": note_id}},
        raison_changement="Assignation d'une note"
    )
    db.add(history)
    db.commit()
    db.refresh(eleve)
    return eleve

# 🔹 Supprimer un élève (optionnel)
@router.delete("/{eleve_id}")
def delete_eleve(
    eleve_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    db.delete(eleve)
    db.commit()
    return {"detail": "Élève supprimé"}

# 🔹 Déassigner une note d'un élève
@router.put("/{eleve_id}/unassign_note", response_model=EleveOut)
def unassign_note_from_eleve(
    eleve_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    old_note_id = eleve.note_id
    if old_note_id is None:
        raise HTTPException(status_code=400, detail="Aucune note assignée à cet élève")

    eleve.note_id = None
    eleve.date_note_assignee = None
    eleve.updated_by = current_user.id
    eleve.updated_at = datetime.utcnow()
    db.add(eleve)

    # Historique
    history = EleveHistory(
        eleve_id=eleve.id,
        edited_by=current_user.id,
        edited_at=datetime.utcnow(),
        changes={"note_id": {"old": old_note_id, "new": None}},
        raison_changement="Désassignation de la note"
    )
    db.add(history)
    db.commit()
    db.refresh(eleve)
    return eleve

