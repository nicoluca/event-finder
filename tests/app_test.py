import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_index_page(client):
    with client:
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200

def test_login_page(client):
    with client:
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200

def test_register_page(client):
    with client:
        response = client.get('/register', follow_redirects=True)
        assert response.status_code == 200

def test_logout_page(client):
    with client:
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

def test_register_password_mismatch(client):
    response = client.post("/register", data={"username": "testuser", "email": "testuser@example.com", "password": "password", "confirmation": "mismatch"})
    assert response.status_code == 403
    assert b"Passwords do not match." in response.data

def test_register_invalid_email(client):
    response = client.post("/register", data={"username": "testuser", "email": "testuserexample.com", "password": "password", "confirmation": "password"})
    assert response.status_code == 403
    assert b"Please provide a valid email." in response.data