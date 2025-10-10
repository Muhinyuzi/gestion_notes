from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from db import get_db
from models import Utilisateur
from schemas import UtilisateurCreate, UtilisateurOut, UtilisateurDetailOut
from passlib.context import CryptContext
from auth import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# ---------------- CREATE USER ----------------
@router.post("/", response_model=UtilisateurOut)
def create_user(user: UtilisateurCreate, db: Session = Depends(get_db),
                current_user: Utilisateur = Depends(get_current_user)):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs")
    
    hashed = hash_password(user.mot_de_passe)
    new_user = Utilisateur(
        nom=user.nom,
        email=user.email,
        mot_de_passe=hashed,
        equipe=user.equipe,
        type=user.type or "user",
        poste=user.poste,
        telephone=user.telephone,
        adresse=user.adresse,
        date_embauche=user.date_embauche
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UtilisateurOut.from_orm(new_user)  # ✅ transformer en Pydantic

# ---------------- LIST USERS ----------------
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
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs")

    query = db.query(Utilisateur)
    if nom:
        query = query.filter(Utilisateur.nom.ilike(f"%{nom}%"))
    if email:
        query = query.filter(Utilisateur.email.ilike(f"%{email}%"))
    if equipe:
        query = query.filter(Utilisateur.equipe.ilike(f"%{equipe}%"))
    if type_:
        query = query.filter(Utilisateur.type.ilike(f"%{type_}%"))

    if sort == "nom_asc":
        query = query.order_by(Utilisateur.nom.asc())
    elif sort == "nom_desc":
        query = query.order_by(Utilisateur.nom.desc())
    elif sort == "date_asc":
        query = query.order_by(Utilisateur.date.asc())
    else:
        query = query.order_by(Utilisateur.date.desc())

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "users": [UtilisateurOut.from_orm(u) for u in users]  # ✅ transformer
    }

# ---------------- USER DETAIL ----------------
@router.get("/{user_id}", response_model=UtilisateurDetailOut)
def get_user_detail(user_id: int, db: Session = Depends(get_db),
                    current_user: Utilisateur = Depends(get_current_user)):
    if current_user.type != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    user = db.query(Utilisateur).options(joinedload(Utilisateur.notes),
                                        joinedload(Utilisateur.commentaires)).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return UtilisateurDetailOut.from_orm(user)  # ✅ transformer

# ---------------- UPDATE USER ----------------
@router.put("/{user_id}", response_model=UtilisateurOut)
def update_user(user_id: int, updated: UtilisateurCreate, db: Session = Depends(get_db),
                current_user: Utilisateur = Depends(get_current_user)):
    if current_user.type != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.nom = updated.nom
    user.email = updated.email
    user.equipe = updated.equipe
    user.type = updated.type or user.type
    user.poste = updated.poste
    user.telephone = updated.telephone
    user.adresse = updated.adresse
    user.date_embauche = updated.date_embauche
    if updated.mot_de_passe:
        user.mot_de_passe = hash_password(updated.mot_de_passe)

    db.commit()
    db.refresh(user)
    return UtilisateurOut.from_orm(user)  # ✅ transformer

# ---------------- DELETE USER ----------------
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: Utilisateur = Depends(get_current_user)):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(user)
    db.commit()
    return None
