import os
import json
import gridfs
import pika
from flask import Flask, request, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from .auth import validate
from .auth_svc import access
from .storage import util

fs_videos = None
fs_mp3s = None
channel = None

def create_app():
    global fs_videos, fs_mp3s, channel

    app = Flask(__name__)

    # Récupération des URI MongoDB depuis les variables d'environnement
    mongo_videos_uri = os.environ.get('MONGODB_VIDEOS_URI')
    mongo_mp3s_uri = os.environ.get('MONGODB_MP3S_URI')

    if not mongo_videos_uri or not mongo_mp3s_uri:
        raise ValueError("Les variables d'environnement MONGODB_VIDEOS_URI et MONGODB_MP3S_URI doivent être définies")

    # Connexion MongoDB avec pymongo
    client_videos = MongoClient(mongo_videos_uri)
    client_mp3s = MongoClient(mongo_mp3s_uri)

    # Création des instances GridFS
    fs_videos = gridfs.GridFS(client_videos.get_default_database())
    fs_mp3s = gridfs.GridFS(client_mp3s.get_default_database())

    # Connexion RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", heartbeat=0))
    channel = connection.channel()

    @app.route("/")
    def root():
        return {"message": "Gateway Service"}, 200

    @app.route("/login", methods=["POST"])
    def login():
        token, err = access.login(request)
        if not err:
            return token
        else:
            return err

    @app.route("/upload", methods=["POST"])
    def upload():
        access_token, err = validate.token(request)
        if err:
            # Assure-toi que unauth_count est défini/importé quelque part
            # unauth_count.inc()
            return err

        access_data = json.loads(access_token)

        if access_data.get("admin"):
            if len(request.files) != 1:
                return "exactly 1 file required", 400

            for _, f in request.files.items():
                err = util.upload(f, fs_videos, channel, access_data)
                if err:
                    return err

            return "success!", 200
        else:
            return "not authorized", 401

    @app.route("/download", methods=["GET"])
    def download():
        access_token, err = validate.token(request)
        if err:
            # unauth_count.inc()
            return err

        access_data = json.loads(access_token)

        if access_data.get("admin"):
            fid_string = request.args.get("fid")
            if not fid_string:
                return "fid is required", 400
            try:
                out = fs_mp3s.get(ObjectId(fid_string))
                return send_file(out, download_name=f"{fid_string}.mp3")
            except Exception as e:
                print(e)
                return "internal server error", 500
        else:
            return "not authorized", 401

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)