import os
import http.client
from http import HTTPStatus

HTTPS = "https"

TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"
AUTH_TOKEN = os.environ.get(TOKEN_ENV_VAR)

OPTIONS = "OPTIONS"
AUTHORIZATION = "Authorization"
EMPTY_PATH = "/"
UTF8 = "utf-8"


class Acquire():

    def __init__(self, conn: http.client.HTTPSConnection):
        self.conn = conn

    def read_remote_csv(self, token: str) -> list[str]:
        conn = self.conn
        try:
            conn.request(OPTIONS, EMPTY_PATH,
                         headers={AUTHORIZATION: f"Bearer {token}"})
            response = conn.getresponse()
            if response.status is HTTPStatus.OK:
                return [line.decode(UTF8) for line in response.readlines()]
            else:
                raise RuntimeError(f"Oops, got a {response.status}")
        finally:
            conn.close()
