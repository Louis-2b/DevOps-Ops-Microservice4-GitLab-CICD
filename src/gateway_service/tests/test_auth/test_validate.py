# tests/test_auth/test_validate.py
import os
import pytest
from unittest.mock import patch
from gateway_service.auth.validate import token

@pytest.fixture
def mock_request():
    class MockRequest:
        headers = {}
    return MockRequest()

def test_token_missing_authorization_header(mock_request):
    """Test quand le header Authorization est manquant"""
    mock_request.headers = {}
    result, error = token(mock_request)
    assert result is None
    assert error == ("missing credentials", 401)

def test_token_empty_authorization(mock_request):
    """Test quand le token est vide"""
    mock_request.headers = {"Authorization": ""}
    result, error = token(mock_request)
    assert result is None
    assert error == ("missing credentials", 401)

@patch.dict(os.environ, {"AUTH_SVC_ADDRESS": "auth-service:5000"})
@patch('requests.post')
def test_token_validation_success(mock_post, mock_request):
    """Test quand la validation du token réussit"""
    # Configurer le mock
    mock_response = type('', (), {})()
    mock_response.status_code = 200
    mock_response.text = "valid_token_content"
    mock_post.return_value = mock_response

    # Appeler la fonction
    mock_request.headers = {"Authorization": "valid_token"}
    result, error = token(mock_request)

    # Vérifications
    assert result == "valid_token_content"
    assert error is None
    mock_post.assert_called_once_with(
        "http://auth-service:5000/validate",
        headers={"Authorization": "valid_token"}
    )

@patch.dict(os.environ, {"AUTH_SVC_ADDRESS": "auth-service:5000"})
@patch('requests.post')
def test_token_validation_failure(mock_post, mock_request):
    """Test quand la validation du token échoue"""
    # Configurer le mock
    mock_response = type('', (), {})()
    mock_response.status_code = 401
    mock_response.text = "invalid token"
    mock_post.return_value = mock_response

    # Appeler la fonction
    mock_request.headers = {"Authorization": "invalid_token"}
    result, error = token(mock_request)

    # Vérifications
    assert result is None
    assert error == ("invalid token", 401)