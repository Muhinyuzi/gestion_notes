from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
import uvicorn
from db import Base, engine, get_db
from models import Utilisateur, Note, Commentaire
from schemas import UtilisateurOut, UtilisateurCreate, UtilisateurDetailOut, NoteOut, CommentaireOut, NoteDetailOut, CommentaireCreate, CommentaireOut
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import auth
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Autoriser Angular (http://localhost:4200)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",  # parfois utile selon ton URL d'accès
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Origines autorisées
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],           # Autoriser tous les headers
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l’API Notes 🚀"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.mot_de_passe):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "equipe": user.equipe
        }}


# ---------------- UTILISATEURS ----------------
@app.post("/utilisateurs")
def create_user(user: dict, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.mot_de_passe)
    new_user = Utilisateur(
        nom=user["nom"],
        email=user["email"],
        mot_de_passe=hashed_pw,
  #  à sécuriser (hash)
        equipe=user["equipe"]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/utilisateurs")
def get_utilisateurs(db: Session = Depends(get_db)):
    utilisateurs = db.query(Utilisateur).all()
    return utilisateurs

@app.get("/utilisateurs/{user_id}", response_model=UtilisateurDetailOut)
def get_utilisateur_detail(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(Utilisateur)
        .options(
            joinedload(Utilisateur.notes),          # charger les notes
            joinedload(Utilisateur.commentaires)   # charger les commentaires
        )
        .filter(Utilisateur.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user

# ---------------- Modifier un utilisateur ----------------
@app.put("/utilisateurs/{user_id}", response_model=UtilisateurOut)
def update_utilisateur(user_id: int, updated_user: UtilisateurCreate, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mettre à jour les champs
    user.nom = updated_user.nom
    user.email = updated_user.email
    user.equipe = updated_user.equipe
    # si tu veux gérer le mot de passe
    if updated_user.mot_de_passe:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user.mot_de_passe = pwd_context.hash(updated_user.mot_de_passe)
    
    db.commit()
    db.refresh(user)
    return user

# ---------------- Supprimer un utilisateur ----------------
@app.delete("/utilisateurs/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utilisateur(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(user)
    db.commit()
    return None  # 204 No Content




# ---------------- NOTES ----------------
@app.post("/notes")
def add_note(note: dict, db: Session = Depends(get_db)):
    new_note = Note(
        titre=note["titre"],
        contenu=note["contenu"],
        equipe=note["equipe"],
        auteur_id=note["auteur_id"]  # ID utilisateur
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@app.get("/notes")
def get_notes(db: Session = Depends(get_db)):
    #notes = db.query(Note).all()
    notes = db.query(Note).options(joinedload(Note.auteur)).all()
    return notes

@app.get("/notes/{note_id}", response_model=NoteDetailOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = (
        db.query(Note)
        .options(
            joinedload(Note.auteur),           # inclure l'auteur
            joinedload(Note.commentaires).joinedload(Commentaire.auteur)  # inclure les commentaires + auteur
        )
        .filter(Note.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# ---------------- COMMENTAIRES ----------------
@app.post("/notes/{note_id}/commentaires", response_model=CommentaireOut)
def add_commentaire(note_id: int, commentaire: CommentaireCreate, db: Session = Depends(get_db)):
    # Vérifier que la note existe
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Vérifier que l'auteur existe
    auteur = db.query(Utilisateur).filter(Utilisateur.id == commentaire.auteur_id).first()
    if not auteur:
        raise HTTPException(status_code=404, detail="Auteur not found")

    # Créer le commentaire
    new_comment = Commentaire(
        contenu=commentaire.contenu,
        auteur_id=commentaire.auteur_id,
        note_id=note_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/notes/{note_id}/commentaires", response_model=List[CommentaireOut])
def get_commentaires(note_id: int, db: Session = Depends(get_db)):
    commentaires = (
        db.query(Commentaire)
        .options(joinedload(Commentaire.auteur))  # 👈 pour inclure l’auteur
        .filter(Commentaire.note_id == note_id)
        .all()
    )
    return commentaires

# ---------------- MODIFIER UNE NOTE ----------------
@app.put("/notes/{note_id}", response_model=NoteDetailOut)
def update_note(note_id: int, note_data: dict, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.titre = note_data.get("titre", note.titre)
    note.contenu = note_data.get("contenu", note.contenu)
    note.equipe = note_data.get("equipe", note.equipe)
    db.commit()
    db.refresh(note)
    return note

# ---------------- SUPPRIMER UNE NOTE ----------------
@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"detail": "Note supprimée"}

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)