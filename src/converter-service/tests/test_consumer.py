import pytest
from unittest.mock import Mock
from consumer import main, callback

@pytest.fixture
def mock_dependencies(mocker):
    # Simuler MongoClient et GridFS
    mock_client = mocker.Mock()
    mock_db_videos = mocker.Mock()
    mock_db_mp3s = mocker.Mock()
    mock_fs_videos = mocker.Mock()
    mock_fs_mp3s = mocker.Mock()

    mocker.patch('consumer.MongoClient', return_value=mock_client)
    mock_client.videos = mock_db_videos
    mock_client.mp3s = mock_db_mp3s
    mocker.patch('consumer.gridfs.GridFS', side_effect=[mock_fs_videos, mock_fs_mp3s])

    # Simuler connexion RabbitMQ
    mock_connection = mocker.Mock()
    mock_channel = mocker.Mock()
    mocker.patch('consumer.pika.BlockingConnection', return_value=mock_connection)
    mock_connection.channel.return_value = mock_channel

    return {
        'client': mock_client,
        'fs_videos': mock_fs_videos,
        'fs_mp3s': mock_fs_mp3s,
        'channel': mock_channel,
        'connection': mock_connection
    }

def test_callback_success(mocker):
    mock_channel = Mock()
    mock_method = Mock(delivery_tag=1)
    mock_properties = Mock()
    body = b"test_file.mp4"
    mock_fs_videos = Mock()
    mock_fs_mp3s = Mock()

    mocker.patch('consumer.to_mp3.start', return_value=None)

    callback(mock_channel, mock_method, mock_properties, body, mock_fs_videos, mock_fs_mp3s)

    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
    mock_channel.basic_nack.assert_not_called()

def test_callback_failure(mocker):
    mock_channel = Mock()
    mock_method = Mock(delivery_tag=1)
    mock_properties = Mock()
    body = b"test_file.mp4"
    mock_fs_videos = Mock()
    mock_fs_mp3s = Mock()

    mocker.patch('consumer.to_mp3.start', return_value="Erreur de conversion")

    callback(mock_channel, mock_method, mock_properties, body, mock_fs_videos, mock_fs_mp3s)

    mock_channel.basic_nack.assert_called_once_with(delivery_tag=1)
    mock_channel.basic_ack.assert_not_called()

def test_main_setup(mocker, mock_dependencies):
    mocker.patch('os.environ.get', side_effect=lambda key: {
        'MONGODB_URI': 'mongodb://localhost:27017',
        'VIDEO_QUEUE': 'video_queue'
    }[key])

    mock_dependencies['channel'].start_consuming.side_effect = KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        main()

    mock_dependencies['connection'].channel.assert_called_once()
    mock_dependencies['channel'].basic_consume.assert_called_once()
    mock_dependencies['channel'].start_consuming.assert_called_once()