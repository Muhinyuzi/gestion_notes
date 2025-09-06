from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn
from db import Base, engine, get_db
from models import Utilisateur, Note, Commentaire


Base.metadata.create_all(bind=engine)

app = FastAPI()


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
    notes = db.query(Note).all()
    return notes

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

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)