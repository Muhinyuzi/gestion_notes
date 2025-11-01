from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine
import uvicorn
from app.config import settings

# ------------------------- Routers -------------------------
from app.routers import utilisateurs, notes, commentaires, login, eleves

# ------------------------- Création des tables -------------------------
Base.metadata.create_all(bind=engine)

# ------------------------- FastAPI App -------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour gérer les employés, notes et commentaires",
    version="1.0.0"
)

# ------------------------- CORS -------------------------
# ✅ Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
print("✅ CORS LOADED WITH:", settings.CORS_ORIGINS)

# 🔹 Pour servir les avatars stockés localement
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ------------------------- Root -------------------------
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l’API Notes & Gestion Utilisateurs 🚀"}

# ------------------------- Inclusion des routers -------------------------
app.include_router(login.router)
app.include_router(utilisateurs.router, prefix="/utilisateurs", tags=["Utilisateurs"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(commentaires.router, prefix="", tags=["Commentaires"])  # endpoints commentaires intégrés aux notes
app.include_router(eleves.router, prefix="/eleves", tags=["eleves"])

# ------------------------- Lancer l'app -------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
