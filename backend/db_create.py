from sqlalchemy import text
from sqlalchemy.orm import Session
from db import engine, Base
from models import Utilisateur, Note, Commentaire, FichierNote
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import os

# 🔐 Hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📁 Répertoire pour fichiers attachés
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔗 Crée la session
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

    # ======================================================
    # 1️⃣ Création des utilisateurs
    # ======================================================
    users_data = [
        {"nom": "Alice", "email": "alice@example.com", "mot_de_passe": "alice123", "type": "admin", "equipe": "Dev", "poste": "Chef de projet", "telephone": "514-123-4567", "adresse": "123 rue Sainte-Catherine, Montréal", "date_embauche": datetime(2023, 1, 10)},
        {"nom": "Bob", "email": "bob@example.com", "mot_de_passe": "bob123", "type": "user", "equipe": "QA", "poste": "Testeur", "telephone": "438-987-6543", "adresse": "55 boulevard René-Lévesque, Laval", "date_embauche": datetime(2022, 5, 22)},
        {"nom": "Charlie", "email": "charlie@example.com", "mot_de_passe": "charlie123", "type": "user", "equipe": "DevOps", "poste": "Ingénieur DevOps", "telephone": "450-888-9999", "adresse": "88 avenue du Parc, Longueuil", "date_embauche": datetime(2021, 8, 30)},
    ]

    users = []
    for u in users_data:
        avatar_num = random.randint(1, 70)
        user = Utilisateur(
            nom=u["nom"],
            email=u["email"],
            mot_de_passe=hash_password(u["mot_de_passe"]),
            type=u["type"],
            equipe=u["equipe"],
            poste=u["poste"],
            telephone=u["telephone"],
            adresse=u["adresse"],
            date_embauche=u["date_embauche"],
            avatar_url=f"https://i.pravatar.cc/150?img={avatar_num}"
        )
        session.add(user)
        users.append(user)
    session.commit()
    print(f"✅ {len(users)} utilisateurs créés avec succès !")

    # ======================================================
    # 2️⃣ Création des notes
    # ======================================================
    notes = []
    now = datetime.utcnow()
    for i in range(20):
        note = Note(
            titre=f"Note {i+1}",
            contenu=f"Contenu de la note {i+1}. C'est un exemple de texte pour tester le résumé IA et les fichiers.",
            equipe=random.choice(["Dev", "QA", "DevOps"]),
            auteur=random.choice(users),
            created_at=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            updated_at=now,
            nb_vues=random.randint(0, 200),
            likes=random.randint(0, 50),
            resume_ia=None
        )
        session.add(note)
        notes.append(note)
    session.commit()
    print(f"✅ {len(notes)} notes créées avec succès !")

    # ======================================================
    # 3️⃣ Fichiers attachés
    # ======================================================
    fichiers = []
    for note in notes:
        # fichiers texte
        for j in range(random.randint(0, 2)):
            filename = f"{note.titre.replace(' ', '_')}_file{j+1}.txt"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "w") as f:
                f.write(f"Fichier attaché pour {note.titre}, fichier {j+1}")
            fichier = FichierNote(nom_fichier=filename, chemin=filepath, note_id=note.id)
            session.add(fichier)
            fichiers.append(fichier)

        # fichiers images simulés
        for img_name in ["sample1.png", "sample2.jpg"]:
            if random.random() > 0.5:
                filename = f"{note.titre.replace(' ', '_')}_{img_name}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(os.urandom(1024))  # Contenu binaire simulé
                fichier = FichierNote(nom_fichier=filename, chemin=filepath, note_id=note.id)
                session.add(fichier)
                fichiers.append(fichier)
    session.commit()
    print(f"✅ {len(fichiers)} fichiers attachés créés avec succès !")

    # ======================================================
    # 4️⃣ Commentaires
    # ======================================================
    commentaires = []
    for note in notes:
        for _ in range(random.randint(0, 3)):
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
