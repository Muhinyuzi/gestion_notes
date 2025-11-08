# app/seed.py
from __future__ import annotations
from datetime import datetime, timedelta
import os
import random

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.db import engine, Base
from app.models.utilisateur import Utilisateur
from app.models.note import Note
from app.models.commentaire import Commentaire
from app.models.fichier import FichierNote
from app.models.eleve import Eleve, EleveHistory
from passlib.context import CryptContext

# 🔐 Hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📁 Répertoire pour fichiers attachés
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔗 Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def reset_schema():
    print("💣 Drop & Create schema…")
    # ✅ plus robuste que des DROP TABLE manuels
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Schema recréé")

def seed():
    reset_schema()
    with SessionLocal() as session:
        # ======================================================
        # 1️⃣ Utilisateurs (inactifs par défaut)
        # ======================================================
        # NOTE: mots de passe = 8 caractères
        users_data = [
            {
                "nom": "Alice", "email": "alice@example.com", "mot_de_passe": "alice123",  # 8 chars
                "type": "admin", "equipe": "Dev", "poste": "Chef de projet",
                "telephone": "514-123-4567", "adresse": "123 rue Sainte-Catherine, Montréal",
                "date_embauche": datetime(2023, 1, 10),
                # 🟡 Option: activer l’admin si tu veux un compte utilisable tout de suite :
                "is_active": True
            },
            {
                "nom": "Bob", "email": "bob@example.com", "mot_de_passe": "bob12345",  # 8 chars
                "type": "user", "equipe": "QA", "poste": "Testeur",
                "telephone": "438-987-6543", "adresse": "55 boulevard René-Lévesque, Laval",
                "date_embauche": datetime(2022, 5, 22),
                "is_active": True
            },
            {
                "nom": "Charlie", "email": "charlie@example.com", "mot_de_passe": "charl123",  # 8 chars
                "type": "user", "equipe": "DevOps", "poste": "Ingénieur DevOps",
                "telephone": "450-888-9999", "adresse": "88 avenue du Parc, Longueuil",
                "date_embauche": datetime(2021, 8, 30),
                "is_active": False
            },
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
                avatar_url=f"https://i.pravatar.cc/150?img={avatar_num}",
                is_active=u.get("is_active", False),  # ✅ important pour activation email
            )
            session.add(user)
            users.append(user)
        session.commit()
        print(f"✅ {len(users)} utilisateurs créés")

        # ======================================================
        # 2️⃣ Notes
        # ======================================================
        created_notes = []
        now = datetime.utcnow()
        for i in range(20):
            note = Note(
                titre=f"Note {i+1}",
                contenu=f"Contenu de la note {i+1}. Exemple de texte pour tests.",
                equipe=random.choice(["Dev", "QA", "DevOps"]),
                auteur=random.choice(users),
                created_at=now - timedelta(days=random.randint(0, 30)),
                updated_at=now,
                nb_vues=random.randint(0, 200),
                likes=random.randint(0, 50),
            )
            session.add(note)
            created_notes.append(note)
        session.commit()
        print(f"✅ {len(created_notes)} notes créées")

        # ======================================================
        # 3️⃣ Fichiers attachés
        # ======================================================
        fichiers = []
        for note in created_notes:
            for j in range(random.randint(0, 2)):
                filename = f"{note.titre.replace(' ', '_')}_file{j+1}.txt"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Fichier attaché pour {note.titre}, fichier {j+1}")
                fichier = FichierNote(nom_fichier=filename, chemin=filepath, note_id=note.id)
                session.add(fichier)
                fichiers.append(fichier)
        session.commit()
        print(f"✅ {len(fichiers)} fichiers attachés créés")

        # ======================================================
        # 4️⃣ Commentaires
        # ======================================================
        commentaires = []
        for note in created_notes:
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
        print(f"✅ {len(commentaires)} commentaires créés")

        # ======================================================
        # 5️⃣ Élèves
        # ======================================================
        eleves_data = [
            {"nom": "Durand", "prenom": "Émilie", "adresse": "22 rue Saint-Denis, Montréal"},
            {"nom": "Tremblay", "prenom": "Marc", "adresse": "14 avenue Papineau, Laval"},
            {"nom": "Nguyen", "prenom": "Sophie", "adresse": "66 boulevard Saint-Laurent, Longueuil"},
            {"nom": "Smith", "prenom": "John", "adresse": "99 rue Sherbrooke, Montréal"},
            {"nom": "Dubois", "prenom": "Camille", "adresse": "5 rue Ontario, Montréal"},
            {"nom": "Lefebvre", "prenom": "Alexandre", "adresse": "23 rue de la Montagne, Laval"},
        ]

        eleves = []
        for data in eleves_data:
            note = random.choice(created_notes) if random.random() > 0.5 else None
            createur = random.choice(users)

            eleve = Eleve(
                nom=data["nom"],
                prenom=data["prenom"],
                adresse=data["adresse"],
                actif=random.choice([True, True, False]),
                note_id=note.id if note else None,
                date_note_assignee=datetime.utcnow() if note else None,
                created_by=createur.id,
                updated_by=None
            )
            session.add(eleve)
            eleves.append(eleve)

        session.commit()
        print(f"✅ {len(eleves)} élèves créés")

        # ======================================================
        # 6️⃣ Historique des élèves
        # ======================================================
        histories = []
        for eleve in eleves:
            if random.random() > 0.4:
                editor = random.choice(users)
                change_type = random.choice([
                    "Modification de l'adresse", "Changement de note", "Réactivation"
                ])

                change_dict = {}
                if "adresse" in change_type:
                    change_dict["adresse"] = {
                        "old": eleve.adresse,
                        "new": f"{eleve.adresse} (modifiée)"
                    }
                if "note" in change_type:
                    change_dict["note_id"] = {
                        "old": eleve.note_id,
                        "new": None
                    }

                history = EleveHistory(
                    eleve_id=eleve.id,
                    edited_by=editor.id,
                    edited_at=datetime.utcnow() - timedelta(days=random.randint(0, 15)),
                    raison_changement=change_type,
                    changes=change_dict
                )
                session.add(history)
                histories.append(history)

        session.commit()
        print(f"✅ {len(histories)} historiques d'élèves créés")
        print("🎉 Données initiales insérées avec succès !")

if __name__ == "__main__" and os.getenv("TESTING") != "1":
    seed()
    print("✅ Base de données initialisée hors mode test")
