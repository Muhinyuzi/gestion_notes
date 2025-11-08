from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, UploadFile, BackgroundTasks, status
from fastapi.responses import FileResponse
from app.models.utilisateur import Utilisateur
from app.schemas.schemas import UtilisateurOut, UtilisateurDetailOut
from app.emails import send_activation_email, send_registration_email
from app.config import settings
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os, shutil

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Répertoire pour les avatars
AVATAR_DIR = "uploads/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


# ======================================================
# 🔹 UTILITAIRES
# ======================================================
def _is_admin(user):
    """Retourne True si l’utilisateur est admin"""
    if not user:
        return False
    user_type = getattr(user, "type", None) or (user.get("type") if isinstance(user, dict) else None)
    return (user_type or "").lower() == "admin"


def _user_id(user):
    """Retourne l’ID de l’utilisateur (compatible dict/ORM)"""
    return getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)


# ======================================================
# 🔸 CRÉATION UTILISATEUR
# ======================================================
def create_user_service(user_data, db: Session, current_user, background_tasks: BackgroundTasks):
    # 🧩 Vérifie que seul un admin peut créer un utilisateur
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent créer des utilisateurs."
        )

    # 📧 Vérifie si l'email existe déjà
    if db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà."
        )

    # 🔐 Hash du mot de passe
    hashed_password = pwd_context.hash(user_data.mot_de_passe or "changeme123")

    # 🆕 Création de l’utilisateur
    new_user = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        mot_de_passe=hashed_password,
        equipe=user_data.equipe,
        type=user_data.type or "user",
        poste=user_data.poste,
        telephone=user_data.telephone,
        adresse=user_data.adresse,
        date_embauche=user_data.date_embauche,
        is_active=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🎟️ Génère un token d’activation unique
    token = jwt.encode(
        {
            "sub": new_user.email,
            "type": "activation",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )

    # 📬 Envoi des e-mails en arrière-plan
    try:
        # 👋 Email de bienvenue (avec mot de passe initial)
        background_tasks.add_task(
            send_registration_email,
            new_user.email,
            new_user.nom,
            user_data.mot_de_passe or "changeme123"
        )

        # 🔓 Email d’activation
        background_tasks.add_task(
            send_activation_email,
            new_user.email,
            new_user.nom,
            token
        )
        print(f"📧 Emails planifiés pour {new_user.email} (bienvenue + activation)")

    except Exception as e:
        print(f"⚠️ Erreur lors de la planification des emails : {e}")

    # ✅ Retourne l'utilisateur créé
    return UtilisateurOut.model_validate(new_user)


# ======================================================
# 🔸 LISTER UTILISATEURS
# ======================================================
def list_users_service(nom, email, equipe, type_, sort, page, limit, db: Session, current_user):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs.")

    query = db.query(Utilisateur)

    if nom:
        query = query.filter(Utilisateur.nom.ilike(f"%{nom}%"))
    if email:
        query = query.filter(Utilisateur.email.ilike(f"%{email}%"))
    if equipe:
        query = query.filter(Utilisateur.equipe.ilike(f"%{equipe}%"))
    if type_:
        query = query.filter(Utilisateur.type.ilike(f"%{type_}%"))

    # Tri
    if sort == "nom_desc":
        query = query.order_by(Utilisateur.nom.desc())
    elif sort == "date_asc":
        query = query.order_by(Utilisateur.date)
    elif sort == "date_desc":
        query = query.order_by(Utilisateur.date.desc())
    else:
        query = query.order_by(Utilisateur.nom.asc())

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "users": [UtilisateurOut.model_validate(u) for u in users],
    }


# ======================================================
# 🔸 DÉTAIL UTILISATEUR
# ======================================================
def get_user_detail_service(user_id: int, db: Session, current_user):
    current_id = _user_id(current_user)

    if not _is_admin(current_user) and current_id != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    user = db.query(Utilisateur).options(
        joinedload(Utilisateur.notes),
        joinedload(Utilisateur.commentaires),
    ).filter(Utilisateur.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    return UtilisateurDetailOut.model_validate(user)


# ======================================================
# 🔸 MISE À JOUR UTILISATEUR
# ======================================================
def update_user_service(user_id: int, updated_data, db: Session, current_user):
    current_id = _user_id(current_user)
    if not _is_admin(current_user) and current_id != user_id:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    # ✅ Compatible dict ou Pydantic model
    data = updated_data.dict(exclude_unset=True) if hasattr(updated_data, "dict") else updated_data
    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UtilisateurOut.model_validate(user)


# ======================================================
# 🔸 SUPPRESSION UTILISATEUR
# ======================================================
def delete_user_service(user_id: int, db: Session, current_user):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs.")

    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès."}


# ======================================================
# 🔸 UPLOAD AVATAR
# ======================================================
async def upload_avatar_service(user_id: int, file: UploadFile, db: Session):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    filename = f"user_{user_id}_{file.filename}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_url = f"http://127.0.0.1:8000/uploads/avatars/{filename}"
    db.commit()
    db.refresh(user)

    return {"avatar_url": user.avatar_url}


# ======================================================
# 🔸 GET AVATAR
# ======================================================
async def get_avatar_service(user_id: int, db: Session):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user or not user.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar non trouvé.")

    file_path = user.avatar_url.replace("http://127.0.0.1:8000/", "")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable.")

    return FileResponse(file_path)
