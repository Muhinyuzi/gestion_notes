from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.eleve import Eleve, EleveHistory
from app.models.note import Note
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import EleveOut, EleveCreate, EleveUpdate

# ---------------- CREATE ----------------
def create_eleve_service(eleve_in: EleveCreate, current_user: Utilisateur, db: Session):
    current_user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    eleve = Eleve(**eleve_in.dict(), created_by=current_user_id)
    db.add(eleve)
    db.commit()
    db.refresh(eleve)
    return EleveOut.from_orm(eleve)

# ---------------- READ ----------------
def get_eleve_service(eleve_id: int, db: Session):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    return EleveOut.from_orm(eleve)

def list_eleves_service(skip: int, limit: int, db: Session):
    return db.query(Eleve).offset(skip).limit(limit).all()

# ---------------- UPDATE ----------------
def update_eleve_service(eleve_id: int, eleve_data: EleveUpdate, db: Session):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    update_data = eleve_data.dict(exclude_unset=True)

    if "updated_by" not in update_data or update_data["updated_by"] is None:
        raise HTTPException(status_code=400, detail="updated_by est obligatoire")

    editor_id = update_data["updated_by"]

    changes = {}
    for field, new_value in update_data.items():
        if field == "updated_by":
            continue
        old_value = getattr(eleve, field)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
            setattr(eleve, field, new_value)

    # ❗ Aucun changement = erreur 400 (test attendu)
    if not changes:
        raise HTTPException(status_code=400, detail="Aucun changement détecté")

    eleve.updated_at = datetime.utcnow()
    eleve.updated_by = editor_id

    history = EleveHistory(
        eleve_id=eleve.id,
        edited_by=editor_id,
        edited_at=datetime.utcnow(),
        changes=changes,
        raison_changement="Mise à jour depuis l'API"
    )
    db.add(history)

    db.commit()
    db.refresh(eleve)
    return EleveOut.from_orm(eleve)

# ---------------- ASSIGN NOTE ----------------
def assign_note_service(eleve_id: int, note_id: int, current_user: Utilisateur, db: Session):
    current_user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note non trouvée")

    old_note_id = eleve.note_id
    eleve.note_id = note_id
    eleve.date_note_assignee = datetime.utcnow()
    eleve.updated_by = current_user_id

    history = EleveHistory(
        eleve_id=eleve.id,
        edited_by=current_user_id,
        edited_at=datetime.utcnow(),
        changes={"note_id": {"old": old_note_id, "new": note_id}},
        raison_changement="Assignation d'une note"
    )

    db.add(history)
    db.commit()
    db.refresh(eleve)
    return EleveOut.from_orm(eleve)

# ---------------- UNASSIGN NOTE ----------------
def unassign_note_service(eleve_id: int, current_user: Utilisateur, db: Session):
    current_user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    old_note_id = eleve.note_id
    if old_note_id is None:
        raise HTTPException(status_code=400, detail="Aucune note assignée à cet élève")

    eleve.note_id = None
    eleve.date_note_assignee = None
    eleve.updated_by = current_user_id
    eleve.updated_at = datetime.utcnow()

    history = EleveHistory(
        eleve_id=eleve.id,
        edited_by=current_user_id,
        edited_at=datetime.utcnow(),
        changes={"note_id": {"old": old_note_id, "new": None}},
        raison_changement="Désassignation de la note"
    )

    db.add(history)
    db.commit()
    db.refresh(eleve)
    return EleveOut.from_orm(eleve)

# ---------------- DELETE ----------------
def delete_eleve_service(eleve_id: int, current_user: Utilisateur, db: Session):
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    db.delete(eleve)
    db.commit()
    return {"detail": "Élève supprimé"}

# ---------------- HISTORY ----------------
def get_eleve_history_service(eleve_id: int, db: Session):
    # 👇 MUST check for student existence first
    eleve = db.query(Eleve).filter(Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    history = (
        db.query(EleveHistory)
        .filter(EleveHistory.eleve_id == eleve_id)
        .order_by(EleveHistory.edited_at.desc())
        .all()
    )

    return [
        {
            "id": h.id,
            "edited_at": h.edited_at,
            "edited_by": h.edited_by,
            "changes": h.changes,
            "raison_changement": h.raison_changement
        }
        for h in history
    ]
