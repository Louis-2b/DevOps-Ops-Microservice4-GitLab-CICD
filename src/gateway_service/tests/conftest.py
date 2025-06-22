import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_request():
    """Fixture pour simuler un objet request"""
    class MockRequest:
        def __init__(self, headers=None, auth=None):
            self.headers = headers or {}
            self.authorization = auth
    return MockRequest

@pytest.fixture
def mock_auth():
    """Fixture pour simuler des credentials d'authentification"""
    class MockAuth:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    return MockAuth

@pytest.fixture
def mock_file_storage():
    """Fixture pour simuler le stockage de fichiers"""
    storage = Mock()
    storage.put.return_value = "mocked_file_id"
    storage.delete.return_value = True
    return storage

@pytest.fixture
def mock_rabbitmq_channel():
    """Fixture pour simuler un channel RabbitMQ"""
    channel = Mock()
    channel.basic_publish.return_value = None
    return channel

@pytest.fixture
def sample_file_content():
    """Fixture fournissant un contenu de fichier de test"""
    return b"sample file content"

@pytest.fixture
def sample_access_data():
    """Fixture fournissant des données d'accès de test"""
    return {"username": "test_user", "permissions": ["read", "write"]}