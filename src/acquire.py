import os
import http.client

HTTPS = "https"


TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"
AUTH_TOKEN = os.environ.get(TOKEN_ENV_VAR)

def get_csv(site):
    print(os.environ)
    auth_header = f"Bearer {AUTH_TOKEN}"
    conn = http.client.HTTPSConnection(site)
    conn.request("OPTIONS", "/", headers={"Authorization": auth_header} )
    response = conn.getresponse()
    print("HTTP status: response.status")
    while chunk := response.read(200):
        print(repr(chunk))
    conn.close()