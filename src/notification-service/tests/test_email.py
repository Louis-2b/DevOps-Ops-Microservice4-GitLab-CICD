import pytest
from unittest.mock import patch, MagicMock
import json
from send import email

@patch('send.email.smtplib.SMTP')
def test_notification_success(mock_smtp):
    mock_session = MagicMock()
    mock_smtp.return_value = mock_session

    msg_json = json.dumps({
        "mp3_fid": "file123",
        "username": "user@example.com"
    })

    with patch.dict('os.environ', {
        "GMAIL_ADDRESS": "sender@example.com",
        "GMAIL_PASSWORD": "password123"
    }):
        email.notification(msg_json)

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_session.starttls.assert_called_once()
    mock_session.login.assert_called_once_with("sender@example.com", "password123")
    assert mock_session.send_message.call_count == 1
    mock_session.quit.assert_called_once()

@patch('send.email.smtplib.SMTP')
def test_notification_invalid_json(mock_smtp):
    bad_json = "not a json"
    with pytest.raises(json.JSONDecodeError):
        email.notification(bad_json)

@patch('send.email.smtplib.SMTP')
def test_notification_missing_env_vars(mock_smtp):
    msg_json = json.dumps({
        "mp3_fid": "file123",
        "username": "user@example.com"
    })

    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError):  # <-- ici, on attend ValueError
            email.notification(msg_json)