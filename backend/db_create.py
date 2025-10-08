from sqlalchemy.orm import Session
from db import engine, Base
from models import Utilisateur, Note, Commentaire
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random

# 🔐 Contexte pour hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crée la session
session = Session(bind=engine)

def seed():
    print("💣 Suppression des tables existantes...")
    Base.metadata.drop_all(bind=engine)

    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recréées avec succès !")

    # -------------------------
    # 1) Création des utilisateurs
    # -------------------------
    users_data = [
        {"nom": "Alice", "email": "alice@example.com", "mot_de_passe": "alice123", "type": "admin", "equipe": "Dev"},
        {"nom": "Bob", "email": "bob@example.com", "mot_de_passe": "bob123", "type": "user", "equipe": "QA"},
        {"nom": "Charlie", "email": "charlie@example.com", "mot_de_passe": "charlie123", "type": "user", "equipe": "DevOps"}
    ]

    users = []
    for u in users_data:
        user = Utilisateur(
            nom=u["nom"],
            email=u["email"],
            mot_de_passe=pwd_context.hash(u["mot_de_passe"]),
            type=u["type"],
            equipe=u["equipe"]
        )
        session.add(user)
        users.append(user)

    session.commit()
    print(f"✅ {len(users)} utilisateurs créés avec succès !")

    # -------------------------
    # 2) Création des 25 notes avec created_at différents
    # -------------------------
    notes = []
    now = datetime.utcnow()
    for i in range(25):
        note = Note(
            titre=f"Note {i+1}",
            contenu=f"Contenu de la note {i+1}.",
            equipe=random.choice(["Dev", "QA", "DevOps"]),
            auteur=random.choice(users),
            created_at=now - timedelta(days=25-i, hours=random.randint(0, 23), minutes=random.randint(0, 59)),
            updated_at=None  # Pas encore modifiée
        )
        session.add(note)
        notes.append(note)

    session.commit()
    print(f"✅ {len(notes)} notes créées avec succès !")

    # -------------------------
    # 3) Création des commentaires aléatoires
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
