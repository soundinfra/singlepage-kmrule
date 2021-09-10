# This file contains all the code, constants, and other information required
# to communicate with the Sound//Infra API.
import hashlib
from http.client import HTTPSConnection
from http import HTTPStatus
from os.path import relpath
from pathlib import Path

from src.types import FileSet

AUTHORIZATION = "Authorization"
COMMA = ","
DOMAIN_MAX_LENGTH = 253
DOT = "."
EMPTY_PATH = "/"
GLOB_ALL = "*"
HTTPS = "https"
OPTIONS = "OPTIONS"
READ_BINARY = "rb"
UTF8 = "utf-8"


def hash_file(path: Path) -> str:
    md5 = hashlib.md5()
    md5.update(open(path, READ_BINARY).read())
    return md5.hexdigest()


def build_manifest(publish_dir: str) -> FileSet:
    files = [path for path in Path(publish_dir).rglob(GLOB_ALL)
             if path.is_file()]
    return {relpath(path, publish_dir): hash_file(path)
            for path in sorted(files)}


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


def parse_csv(lines: list[bytes]) -> FileSet:
    result = {}
    for index, line in enumerate(lines, 1):
        try:
            values = line.decode(UTF8).strip().split(COMMA)
            if len(values) < 2:
                raise ValueError(
                    f"Error: Expected two columns on line {index} of CSV.")
            filename = values[1].strip()
            if filename in result:
                raise ValueError(
                    f"Error: Multiple entries for file: {filename}")
            else:
                hash = values[0].strip()
                if not hash.isalnum():
                    raise ValueError(
                        f"Error: Hash on line {index} does not look valid.")
                result[filename] = values[0].strip()
        except UnicodeDecodeError as err:
            raise ValueError(
                f"Error: Decode error on line {index} ({str(err)}).")
    return result


class SoundInfraClient():

    def __init__(self, site: str, conn: HTTPSConnection = None):
        validate_domain_name(site)
        if not conn:
            self.conn = HTTPSConnection(site)
        else:
            self.conn = conn

    def get_remote_csv(self, token: str) -> list[bytes]:
        try:
            headers = {AUTHORIZATION: f"Bearer {token}"}
            self.conn.request(OPTIONS, EMPTY_PATH, headers=headers)
            response = self.conn.getresponse()
            if response.status is HTTPStatus.OK:
                return response.readlines()
            else:
                raise RuntimeError(f"Oops, got a {response.status}")
        finally:
            self.conn.close()

    def get_remote_fileset(self, token: str) -> FileSet:
        return parse_csv(self.get_remote_csv(token))
