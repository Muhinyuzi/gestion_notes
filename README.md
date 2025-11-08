# 📘 Gestion Notes & Employés  
Application complète de gestion d’utilisateurs, d’élèves, de notes et de fichiers, construite avec **FastAPI (backend)** et **Angular (frontend)**.  
Ce projet démontre une architecture moderne, testée, modulaire et prête pour un usage professionnel.

---

## 🚀 Fonctionnalités principales

### ✅ Utilisateurs
- Création, modification, suppression  
- Rôles : **admin** / **user**  
- Activation de compte par email  
- Changement de mot de passe (par utilisateur ou admin)

### ✅ Élèves
- CRUD complet  
- Assignation / désassignation de notes  
- Historique des mises à jour  

### ✅ Notes
- CRUD complet  
- Auteur, contenu, fichiers attachés  
- Recherche, filtre, tri  

### ✅ Commentaires
- Commentaires liés aux notes  
- Auteur, date, contenu  

### ✅ Fichiers
- Upload de documents associés aux notes  
- Stockage et lien automatique

### ✅ Authentification
- JWT (connexion / protection routes)
- Activation par email
- Tests complets Pytest (backend)

---

## 🛠️ Technologies utilisées

### Backend (FastAPI)
- FastAPI
- SQLAlchemy ORM
- Alembic (migrations)
- Pytest (tests automatisés)
- JWT Authentication
- Pydantic v2
- PostgreSQL

### Frontend (Angular)
- Angular 17
- TypeScript / RxJS
- Angular Material
- SCSS / Design moderne

---

## 📂 Architecture du projet

gestion_notes/
│── backend/
│ ├── app/
│ │ ├── routers/ → API (utilisateurs, notes, élèves…)
│ │ ├── models/ → SQLAlchemy ORM
│ │ ├── services/ → Logique métier
│ │ ├── schemas/ → Pydantic
│ │ ├── auth/ → Login, JWT
│ │ ├── tests/ → Pytest (200+ tests)
│── frontend/
├── src/app/
├── components/ → UI, pages
├── services/ → API Angular



---

## ⚙️ Installation & Lancement

### ✅ 1. Backend

```bash
cd backend
uvicorn app.main:app --reload


### ✅ 2. Frontend

cd frontend
ng serve -o

✅ Exécution des tests backend
cd backend
pytest -vv


📌 API disponible

POST /login

POST /utilisateurs/

GET /utilisateurs/

PATCH /auth/change-password

PATCH /auth/admin/change-password/{id}

POST /notes/

GET /notes/

etc.

✅ Activation utilisateur (email simulé en test)

En mode test, les emails ne sont pas envoyés :
ils sont interceptés via unittest.mock.AsyncMock dans conftest.py.

✅ Pourquoi ce projet ?

Ce projet sert :

à démontrer une architecture Full Stack professionnelle

à renforcer un portfolio technique

à servir de base pour un futur produit SaaS

à intégrer ensuite mon IA NeuroBase



📌 Auteur

Jean Claude Muhinyuzi
Développeur Full-Stack | Québec, Canada
GitHub : https://github.com/Muhinyuzi