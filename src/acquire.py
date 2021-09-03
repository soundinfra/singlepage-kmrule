import os
import http.client
from http import HTTPStatus

HTTPS = "https"

TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"
AUTH_TOKEN = os.environ.get(TOKEN_ENV_VAR)

OPTIONS = "OPTIONS"
AUTHORIZATION = "Authorization"
EMPTY_PATH = "/"


class Acquire():

    def __init__(self, conn):
        self.conn = conn

    def read_remote_csv(self, token):
        conn = self.conn
        try:
            conn.request(OPTIONS, EMPTY_PATH,
                         headers={AUTHORIZATION: f"Bearer {token}"})
            response = conn.getresponse()
            if response.status is HTTPStatus.OK:
                return response.readlines()
            else:
                print(f"Oops, got a {response.status}")
        finally:
            conn.close()
        return []
