# app/services/utilisateurs.py
import os
import shutil
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import UtilisateurCreate, UtilisateurOut, UtilisateurDetailOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_password(password: str):
    return pwd_context.hash(password)

# ---------------- CREATE ----------------
def create_user_service(user: UtilisateurCreate, db: Session, current_user: Utilisateur):
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
    return UtilisateurOut.from_orm(new_user)

# ---------------- LIST ----------------
def list_users_service(nom, email, equipe, type_, sort, page, limit, db: Session, current_user: Utilisateur):
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
        "users": [UtilisateurOut.from_orm(u) for u in users]
    }

# ---------------- DETAIL ----------------
def get_user_detail_service(user_id: int, db: Session, current_user: Utilisateur):
    if current_user.type != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    user = db.query(Utilisateur).options(
        joinedload(Utilisateur.notes),
        joinedload(Utilisateur.commentaires)
    ).filter(Utilisateur.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return UtilisateurDetailOut.from_orm(user)

# ---------------- UPDATE ----------------
def update_user_service(user_id: int, updated: UtilisateurCreate, db: Session, current_user: Utilisateur):
    if current_user.type != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    for key, value in updated.dict(exclude_unset=True).items():
        if key == "mot_de_passe" and value:
            user.mot_de_passe = hash_password(value)
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UtilisateurOut.from_orm(user)

# ---------------- DELETE ----------------
def delete_user_service(user_id: int, db: Session, current_user: Utilisateur):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(user)
    db.commit()
    return None

# ---------------- AVATAR UPLOAD ----------------
async def upload_avatar_service(user_id: int, file, db: Session):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")

    file_path = os.path.join(UPLOAD_DIR, f"user_{user_id}_{file.filename}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_url = f"http://127.0.0.1:8000/uploads/avatars/user_{user_id}_{file.filename}"
    db.commit()
    db.refresh(user)
    return {"avatar_url": user.avatar_url}

# ---------------- AVATAR GET ----------------
async def get_avatar_service(user_id: int, db: Session):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="Aucun avatar défini")

    file_path = user.avatar_url.replace("http://127.0.0.1:8000/", "")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

    return FileResponse(file_path)
