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

    def __init__(self, site: str, conn: http.client.HTTPSConnection = None):
        if not site:
            raise ValueError(f"Invalid site name: \"{site}\".")
        if not '.' in site:
            raise ValueError(f"No Top-Level-Domain for site: \"{site}\"")
        if not conn:
            self.conn = http.HTTPSConnection(site)
        else:
            self.conn = conn

    def read_remote_csv(self, token: str) -> list[str]:
        try:
            self.conn.request(OPTIONS, EMPTY_PATH,
                         headers={AUTHORIZATION: f"Bearer {token}"})
            response = self.conn.getresponse()
            if response.status is HTTPStatus.OK:
                return [line.decode(UTF8) for line in response.readlines()]
            else:
                raise RuntimeError(f"Oops, got a {response.status}")
        finally:
            self.conn.close()
