import os
import pytest
from unittest.mock import patch
from gateway_service.auth_svc.access import login

@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self, auth=None):
            self.authorization = auth
    return MockRequest

def test_login_missing_credentials(mock_request):
    """Test quand les credentials sont manquants"""
    request = mock_request(auth=None)
    result, error = login(request)
    assert result is None
    assert error == ("missing credentials", 401)

@patch.dict(os.environ, {"AUTH_SVC_ADDRESS": "auth-service:5000"})
@patch('requests.post')
def test_login_success(mock_post, mock_request):
    """Test quand le login réussit"""
    mock_response = type('', (), {})()
    mock_response.status_code = 200
    mock_response.text = "auth_token"
    mock_post.return_value = mock_response

    class MockAuth:
        username = "test_user"
        password = "test_pass"
    
    request = mock_request(auth=MockAuth())
    result, error = login(request)

    assert result == "auth_token"
    assert error is None
    mock_post.assert_called_once_with(
        "http://auth-service:5000/login",
        auth=("test_user", "test_pass")
    )

@patch.dict(os.environ, {"AUTH_SVC_ADDRESS": "auth-service:5000"})
@patch('requests.post')
def test_login_failure(mock_post, mock_request):
    """Test quand le login échoue"""
    mock_response = type('', (), {})()
    mock_response.status_code = 401
    mock_response.text = "invalid credentials"
    mock_post.return_value = mock_response

    class MockAuth:
        username = "wrong_user"
        password = "wrong_pass"
    
    request = mock_request(auth=MockAuth())
    result, error = login(request)

    assert result is None
    assert error == ("invalid credentials", 401)

@patch.dict(os.environ, {"AUTH_SVC_ADDRESS": "auth-service:5000"})
@patch('requests.post')
def test_login_empty_credentials(mock_post, mock_request):
    """Test avec des credentials vides"""
    mock_response = type('', (), {})()
    mock_response.status_code = 401
    mock_response.text = "invalid credentials"
    mock_post.return_value = mock_response

    class MockAuth:
        username = ""
        password = ""
    
    request = mock_request(auth=MockAuth())
    result, error = login(request)
    
    assert result is None
    assert error[1] == 401  # Le code d'erreur devrait être 401

@patch.dict(os.environ, {}, clear=True)
@patch('requests.post')
def test_login_missing_auth_svc_address(mock_post, mock_request):
    """Test quand AUTH_SVC_ADDRESS n'est pas configuré"""
    class MockAuth:
        username = "test"
        password = "test"
    
    request = mock_request(auth=MockAuth())
    result, error = login(request)
    assert result is None
    assert error[1] == 500  # ou autre code selon ce que renvoie login()