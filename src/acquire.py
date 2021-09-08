from http.client import HTTPSConnection
from http import HTTPStatus

HTTPS = "https"


AUTHORIZATION = "Authorization"
DOMAIN_MAX_LENGTH = 253
DOT = '.'
EMPTY_PATH = "/"
OPTIONS = "OPTIONS"
UTF8 = "utf-8"


def validate_domain_name(name: str) -> None:
    if not name:
        raise ValueError("Domain name cannot be blank.")
    if len(name) > DOMAIN_MAX_LENGTH:
        raise ValueError(f"Domain name is too long ({len(name)} chars, " +
                         f"max is {DOMAIN_MAX_LENGTH})")
    if DOT not in name:
        raise ValueError(f"No Top-Level-Domain found in: \"{name}\"")
    # Check domain name for (incomplete) list of invalid characters.
    for char in name:
        if char in "_!@#$%^&*":
            raise ValueError(f"Invalid character {char} in domain name.")


class Acquire():

    def __init__(self, site: str, conn: HTTPSConnection = None):
        validate_domain_name(site)
        if not conn:
            self.conn = HTTPSConnection(site)
        else:
            self.conn = conn

    def get_remote_csv(self, token: str) -> list[str]:
        try:
            headers = {AUTHORIZATION: f"Bearer {token}"}
            self.conn.request(OPTIONS, EMPTY_PATH, headers=headers)
            response = self.conn.getresponse()
            if response.status is HTTPStatus.OK:
                return [line.decode(UTF8) for line in response.readlines()]
            else:
                raise RuntimeError(f"Oops, got a {response.status}")
        finally:
            self.conn.close()
