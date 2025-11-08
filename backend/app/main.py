import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine  # ✅ use session engine override-aware
from app.config import settings
from app.routers import activation
from app.routers import reset_password



# 🔧 Force le mode production
os.environ["TESTING"] = "0"


# Routers
from app.routers import utilisateurs, notes, commentaires, login, eleves, router_password_change

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Notes & Gestion Utilisateurs",
    version="1.0.0",
)

IS_TEST = os.getenv("TESTING") == "1"

if IS_TEST:
    print("🧪 Startup skipped (TEST mode)")
else:
    print("🚀 Application boot — Production mode")
    Base.metadata.create_all(bind=engine)  # ✅ only in prod


# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ CORS:", settings.CORS_ORIGINS)

# ✅ Static upload dir
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    return {"message": "Bienvenue sur l’API Notes & Gestion Utilisateurs 🚀"}


# ✅ Routers
app.include_router(router_password_change.router)
app.include_router(activation.router)
app.include_router(reset_password.router)
app.include_router(login.router)
app.include_router(utilisateurs.router, prefix="/utilisateurs", tags=["Utilisateurs"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(commentaires.router, tags=["Commentaires"])
app.include_router(eleves.router, prefix="/eleves", tags=["Élèves"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
