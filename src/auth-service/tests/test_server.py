import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from server import server, CreateJWT

# Prépare l'application Flask pour les tests
@pytest.fixture
def client():
    server.config['TESTING'] = True
    with server.test_client() as client:
        yield client

# Simule les variables d'environnement
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('JWT_SECRET', 'mysecretkey')
    monkeypatch.setenv('AUTH_TABLE', 'users')
    monkeypatch.setenv('DATABASE_HOST', 'localhost')
    monkeypatch.setenv('DATABASE_NAME', 'test_db')
    monkeypatch.setenv('DATABASE_USER', 'test_user')
    monkeypatch.setenv('DATABASE_PASSWORD', 'test_pass')

# Simule la base de données
@pytest.fixture
def mock_db(mocker):
    mock_cursor = mocker.patch('psycopg2.connect').return_value.cursor.return_value
    return mock_cursor

# Test 1 : Authentification réussie
def test_login_success(client, mock_env, mock_db):
    # Simule une réponse de la base de données (email et mot de passe corrects)
    mock_db.fetchone.return_value = ('test@example.com', 'password123')
    
    # Envoie une requête avec email:test@example.com et mot de passe:password123
    response = client.post('/login', headers={
        'Authorization': 'Basic dGVzdEBleGFtcGxlLmNvbTpwYXNzd29yZDEyMw=='  # Base64 de test@example.com:password123
    })
    
    # Vérifie que la réponse est un succès (code 200) et contient un JWT
    assert response.status_code == 200
    assert 'eyJ' in response.get_data(as_text=True)  # Un JWT commence par "eyJ"

# Test 2 : Authentification échouée (mauvais mot de passe)
def test_login_failure_wrong_password(client, mock_env, mock_db):
    # Simule une réponse de la base de données
    mock_db.fetchone.return_value = ('test@example.com', 'password123')
    
    # Envoie une requête avec un mauvais mot de passe
    response = client.post('/login', headers={
        'Authorization': 'Basic dGVzdEBleGFtcGxlLmNvbTp3cm9uZw=='  # Base64 de test@example.com:wrong
    })
    
    # Vérifie qu'on reçoit une erreur 401
    assert response.status_code == 401
    assert 'Could not verify' in response.get_data(as_text=True)

# Test 3 : Validation d'un JWT valide
def test_validate_success(client, mock_env):
    # Crée un JWT valide
    token = CreateJWT('test@example.com', 'mysecretkey', True)
    
    # Envoie une requête avec le JWT
    response = client.post('/validate', headers={
        'Authorization': f'Bearer {token}'
    })
    
    # Vérifie que la réponse est un succès et contient l'email
    assert response.status_code == 200
    assert response.json['username'] == 'test@example.com'

# Test 4 : Validation échouée (pas de JWT)
def test_validate_failure_no_token(client, mock_env):
    # Envoie une requête sans JWT
    response = client.post('/validate')
    
    # Vérifie qu'on reçoit une erreur 401
    assert response.status_code == 401
    assert 'Unauthorized' in response.get_data(as_text=True)