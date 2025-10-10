from sqlalchemy import text
from sqlalchemy.orm import Session
from db import engine, Base
from models import Utilisateur, Note, Commentaire, FichierNote
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import os

# 🔐 Contexte pour hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Répertoire pour fichiers attachés
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Crée la session
session = Session(bind=engine)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed():
    print("💣 Suppression des tables existantes avec CASCADE...")
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fichiers_note CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS commentaires CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS notes CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS utilisateurs CASCADE;"))
        conn.commit()

    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recréées avec succès !")

    # -------------------------
    # 1) Création des utilisateurs
    # -------------------------
    users_data = [
        {"nom": "Alice", "email": "alice@example.com", "mot_de_passe": "alice123", "type": "admin", "equipe": "Dev"},
        {"nom": "Bob", "email": "bob@example.com", "mot_de_passe": "bob123", "type": "user", "equipe": "QA"},
        {"nom": "Charlie", "email": "charlie@example.com", "mot_de_passe": "charlie123", "type": "user", "equipe": "DevOps"},
        {"nom": "David", "email": "david@example.com", "mot_de_passe": "david123", "type": "user", "equipe": "Dev"},
        {"nom": "Eva", "email": "eva@example.com", "mot_de_passe": "eva123", "type": "user", "equipe": "QA"},
    ]

    users = []
    for u in users_data:
        user = Utilisateur(
            nom=u["nom"],
            email=u["email"],
            mot_de_passe=hash_password(u["mot_de_passe"]),
            type=u["type"],
            equipe=u["equipe"]
        )
        session.add(user)
        users.append(user)
    session.commit()
    print(f"✅ {len(users)} utilisateurs créés avec succès !")

    # -------------------------
    # 2) Création des notes
    # -------------------------
    notes = []
    now = datetime.utcnow()
    for i in range(20):
        note = Note(
            titre=f"Note {i+1}",
            contenu=f"Contenu de la note {i+1}.",
            equipe=random.choice(["Dev", "QA", "DevOps"]),
            auteur=random.choice(users),
            created_at=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            updated_at=now
        )
        session.add(note)
        notes.append(note)
    session.commit()
    print(f"✅ {len(notes)} notes créées avec succès !")

    # -------------------------
    # 3) Création des fichiers attachés
    # -------------------------
    fichiers = []
    for note in notes:
        nb_files = random.randint(0, 2)
        for j in range(nb_files):
            filename = f"{note.titre.replace(' ', '_')}_file{j+1}.txt"
            filepath = os.path.join(UPLOAD_DIR, filename)
            # Création d'un fichier vide pour le seed
            with open(filepath, "w") as f:
                f.write(f"Fichier attaché pour {note.titre}, fichier {j+1}")

            fichier = FichierNote(
                nom_fichier=filename,
                chemin=filepath,
                note_id=note.id
            )
            session.add(fichier)
            fichiers.append(fichier)
    session.commit()
    print(f"✅ {len(fichiers)} fichiers attachés créés avec succès !")

    # -------------------------
    # 4) Création des commentaires
    # -------------------------
    commentaires = []
    for note in notes:
        nb_comments = random.randint(0, 3)
        for _ in range(nb_comments):
            com = Commentaire(
                contenu=f"Commentaire pour {note.titre}",
                auteur=random.choice(users),
                note=note,
                date=note.created_at + timedelta(hours=random.randint(0, 5))
            )
            session.add(com)
            commentaires.append(com)
    session.commit()
    print(f"✅ {len(commentaires)} commentaires créés avec succès !")

seed()
