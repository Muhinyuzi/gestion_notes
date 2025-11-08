# app/tests/test_service_eleves.py
import pytest
from app.tests.conftest import TestingSessionLocal
from app.services.eleves import (
    create_eleve_service,
    list_eleves_service,
    get_eleve_service,  # ✅ bon nom
    update_eleve_service,
    delete_eleve_service
)
from app.models.eleve import Eleve
from app.schemas.schemas import EleveCreate, EleveUpdate

# 🧩 Fake admin pour simuler un utilisateur connecté
class FakeAdmin:
    id = 1
    type = "admin"
    equipe = "Dev"

fake_admin = FakeAdmin()

@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


def test_create_eleve_service(db):
    """✅ Création d’un élève"""
    data = EleveCreate(
        nom="John",
        prenom="Doe",
        adresse="Montréal",
        actif=True,
        en_attente=False
    )
    eleve = create_eleve_service(data, fake_admin, db)
    assert eleve.nom == "John"
    assert eleve.prenom == "Doe"


def test_list_eleves_service(db):
    """✅ Liste des élèves"""
    data = EleveCreate(
        nom="Jane",
        prenom="Doe",
        adresse="Québec",
        actif=True,
        en_attente=False
    )
    create_eleve_service(data, fake_admin, db)

    result = list_eleves_service(0, 20, db)
    assert len(result) >= 1


def test_get_eleve_service(db):
    """✅ Récupération d’un élève"""
    data = EleveCreate(
        nom="Bob",
        prenom="Smith",
        adresse="Laval",
        actif=True,
        en_attente=False
    )
    e = create_eleve_service(data, fake_admin, db)
    detail = get_eleve_service(e.id, db)
    assert detail.id == e.id


def test_update_eleve_service(db):
    """✅ Mise à jour d’un élève"""
    data = EleveCreate(
        nom="Alex",
        prenom="Kim",
        adresse="Gatineau",
        actif=True,
        en_attente=False
    )
    e = create_eleve_service(data, fake_admin, db)

    update = EleveUpdate(adresse="Montréal", updated_by=fake_admin.id)
    updated = update_eleve_service(e.id, update, db)
    assert updated.adresse == "Montréal"


def test_delete_eleve_service(db):
    """✅ Suppression d’un élève"""
    data = EleveCreate(
        nom="Léa",
        prenom="Martin",
        adresse="Sherbrooke",
        actif=True,
        en_attente=False
    )
    e = create_eleve_service(data, fake_admin, db)
    delete_eleve_service(e.id, fake_admin, db)
    assert db.query(Eleve).count() == 0
