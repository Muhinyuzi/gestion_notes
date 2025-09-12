from sqlalchemy.orm import Session
from db import engine, Base
from models import Utilisateur, Note, Commentaire
from passlib.context import CryptContext
from datetime import datetime

# 🔐 Contexte pour hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crée la session
session = Session(bind=engine)

def seed():

    print("💣 Suppression des tables existantes...")
    Base.metadata.drop_all(bind=engine)

    # ⚡ Crée toutes les tables à partir des modèles
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
    # 2) Création des notes
    # -------------------------
    notes_data = [
        {"titre": "Première Note", "contenu": "Contenu de la première note.", "equipe": "Dev", "auteur": users[0]},
        {"titre": "Deuxième Note", "contenu": "Contenu de la deuxième note.", "equipe": "QA", "auteur": users[1]},
    ]

    notes = []
    for n in notes_data:
        note = Note(
            titre=n["titre"],
            contenu=n["contenu"],
            equipe=n["equipe"],
            auteur=n["auteur"]
        )
        session.add(note)
        notes.append(note)

    session.commit()
    print(f"✅ {len(notes)} notes créées avec succès !")

    # -------------------------
    # 3) Création des commentaires
    # -------------------------
    commentaires_data = [
        {"contenu": "Super note !", "auteur": users[1], "note": notes[0]},
        {"contenu": "Je vais vérifier ça.", "auteur": users[2], "note": notes[0]},
        {"contenu": "Bonne explication.", "auteur": users[0], "note": notes[1]},
    ]

    commentaires = []
    for c in commentaires_data:
        com = Commentaire(
            contenu=c["contenu"],
            auteur=c["auteur"],
            note=c["note"],
            date=datetime.utcnow()
        )
        session.add(com)
        commentaires.append(com)

    session.commit()
    print(f"✅ {len(commentaires)} commentaires créés avec succès !")

seed()