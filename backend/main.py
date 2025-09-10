from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload
import uvicorn
from db import Base, engine, get_db
from models import Utilisateur, Note, Commentaire
from schemas import UtilisateurOut, NoteOut, CommentaireOut, NoteDetailOut
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


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

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l’API Notes 🚀"}


# ---------------- UTILISATEURS ----------------
@app.post("/utilisateurs")
def create_user(user: dict, db: Session = Depends(get_db)):
    new_user = Utilisateur(
        nom=user["nom"],
        email=user["email"],
        mot_de_passe=user["mot_de_passe"],  #  à sécuriser (hash)
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
@app.post("/notes/{note_id}/commentaires")
def add_commentaire(note_id: int, commentaire: dict, db: Session = Depends(get_db)):
    new_comment = Commentaire(
        contenu=commentaire["contenu"],
        auteur_id=commentaire["auteur_id"],
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

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)