import json
import pika

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        print(err)
        return "internal server error, fs level", 500

    username = access.get("username")  # Utiliser get pour éviter KeyError

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": username,
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        print(err)
        try:
            fs.delete(fid)
        except Exception as err_del:
            print(err_del)
        return "internal server error rabbitmq issue", 500

    return None  # Succès, aucune erreur