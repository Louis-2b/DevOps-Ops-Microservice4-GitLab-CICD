import os
import requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    auth_svc_address = os.environ.get('AUTH_SVC_ADDRESS')
    if not auth_svc_address:
        # Retourne une erreur claire si l'adresse n'est pas configurée
        return None, ("AUTH_SVC_ADDRESS not configured", 500)

    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{auth_svc_address}/login", auth=basicAuth
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)