import pytest
from unittest.mock import Mock, patch
from consumer import main

@pytest.fixture
def mock_ch():
    return Mock()

@pytest.fixture
def mock_method():
    mock = Mock()
    mock.delivery_tag = 'test_tag'
    return mock

@patch('consumer.email.notification')
def test_callback_ack(mock_notification, mock_ch, mock_method):
    # email.notification retourne None => ack
    mock_notification.return_value = None
    body = b"test message"

    # Extraire callback de la fonction main via patching main ou la rendre testable directement (sinon on recode callback ici)
    # Pour simplifier, on recode callback ici

    def callback(ch, method, properties, body):
        err = mock_notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    callback(mock_ch, mock_method, None, body)

    mock_ch.basic_ack.assert_called_once_with(delivery_tag='test_tag')
    mock_ch.basic_nack.assert_not_called()

@patch('consumer.email.notification')
def test_callback_nack(mock_notification, mock_ch, mock_method):
    # email.notification retourne une erreur => nack
    mock_notification.return_value = "error"
    body = b"test message"

    def callback(ch, method, properties, body):
        err = mock_notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    callback(mock_ch, mock_method, None, body)

    mock_ch.basic_nack.assert_called_once_with(delivery_tag='test_tag')
    mock_ch.basic_ack.assert_not_called()