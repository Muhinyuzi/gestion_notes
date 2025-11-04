from app.auth import get_current_user
from app.main import app
def test_create_user(client):
    response = client.post("/utilisateurs/", json={
        "nom": "Alice",
        "email": "alice@test.com",
        "mot_de_passe": "1234",
        "type": "admin",
        "equipe": "Dev"
    })

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "alice@test.com"
    assert data["nom"] == "Alice"

# ✅ Override auth: simulate admin during tests
def override_get_current_user():
    class TestUser:
        id = 1
        nom = "Test Admin"
        email = "admin@test.com"
        type = "admin"
        equipe = "Dev"

    return TestUser()
 
app.dependency_overrides[get_current_user] = override_get_current_user 