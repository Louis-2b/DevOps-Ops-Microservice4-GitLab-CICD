import pytest
import os
from unittest.mock import patch, MagicMock

# Définit les variables d'environnement AVANT l'import
os.environ['MONGODB_VIDEOS_URI'] = 'mongodb://localhost:27017/testdb_videos'
os.environ['MONGODB_MP3S_URI'] = 'mongodb://localhost:27017/testdb_mp3s'

# Mock pika.BlockingConnection pour qu'il ne tente pas de se connecter à RabbitMQ
@pytest.fixture(scope='module', autouse=True)
def mock_rabbitmq():
    with patch('gateway_service.server.pika.BlockingConnection') as mock_conn:
        mock_conn.return_value = MagicMock()
        yield

from gateway_service.server import create_app

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "Gateway Service"}

def test_login_post_empty(client):
    response = client.post("/login", data={})
    assert response.status_code != 500