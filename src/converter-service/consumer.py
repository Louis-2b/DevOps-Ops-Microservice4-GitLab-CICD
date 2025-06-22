import pika
import sys
import os
from pymongo import MongoClient
import gridfs
from convert import to_mp3
from functools import partial

def main():
    client = MongoClient(os.environ.get('MONGODB_URI'))
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', heartbeat=0)
    )
    channel = connection.channel()

    # Partial to pass fs_videos and fs_mp3s to callback
    wrapped_callback = partial(callback, fs_videos=fs_videos, fs_mp3s=fs_mp3s)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=wrapped_callback
    )

    print("Waiting for messages, to exit press CTRL+C")

    channel.start_consuming()

def callback(ch, method, properties, body, fs_videos, fs_mp3s):
    err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
    if err:
        ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)