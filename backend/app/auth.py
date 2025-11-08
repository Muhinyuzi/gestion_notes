# app/auth.py
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.utilisateur import Utilisateur

# ==========================================================
# 🔹 CONFIGURATION GÉNÉRALE
# ==========================================================
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ACTIVATION_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_HOURS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ==========================================================
# 🔹 HASH / VERIFY MOTS DE PASSE
# ==========================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================================
# 🔹 TOKEN D’ACCÈS (connexion)
# ==========================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crée un token JWT signé (utilisé pour la connexion)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retourne l'utilisateur courant.
    - En production : retourne un objet ORM complet
    - En tests : reste compatible avec les dicts utilisés
    """
    from app.config import settings
    from jose import JWTError, jwt
    from fastapi import HTTPException, status

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = None
    if str(sub).isdigit():
        user = db.query(Utilisateur).filter(Utilisateur.id == int(sub)).first()
    if not user:
        user = db.query(Utilisateur).filter(Utilisateur.email == sub).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # 🔐 Si on est en mode test : retourne un dict
    if os.getenv("TESTING") == "1":
        return {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "type": user.type,
            "equipe": user.equipe,
            "is_active": getattr(user, "is_active", False),
        }

    # 🟢 En exécution normale : retourne un vrai ORM object
    return user



# ==========================================================
# 🔹 TOKEN D’ACTIVATION DE COMPTE
# ==========================================================
def create_activation_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)
    payload = {"sub": email, "exp": expire, "type": "activation"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_activation_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "activation":
            return None
        return payload.get("sub")
    except JWTError:
        return None


# ==========================================================
# 🔹 TOKEN DE RÉINITIALISATION DE MOT DE PASSE
# ==========================================================
def create_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    payload = {"sub": email, "exp": expire, "type": "reset"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
