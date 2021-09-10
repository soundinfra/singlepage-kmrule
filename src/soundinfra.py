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
    '''
        Hash a local file the same way Sound//Infra does for the manifest CSV.

    :param path:    The path of the file to hash.
    :return:        An MD5 hex digest string.
    '''
    #
    md5 = hashlib.md5()
    md5.update(open(path, READ_BINARY).read())
    return md5.hexdigest()


def build_manifest(directory: str) -> FileSet:
    '''
    Build a local manifest in the same fashion that Sound//Infra generates a
    manifest CSV for a site powered by Sound//Infra.

    Basically this function recursively takes a MD5 hash of every file under
    'directory' and returns a dictionary of path -> hash.

    E.g. if the 'public' directory contains the following two files:
    ```
     /public
        index.html
        static/common.css
    ```

    Then `build_manifest("public")` will return:
        FileSet {
            "index.html": "1213abcef4...",
            "static/common.css": "abcf14334..."
        }

        Parameters:
            directory (str): The directory representing the local site root.
        Returns:
            manifest (FileSet): A dictionary of path -> hash pairs.
    '''
    files = [path for path in Path(directory).rglob(GLOB_ALL)
             if path.is_file()]
    manifest = {relpath(path, directory): hash_file(path)
                for path in sorted(files)}
    return manifest


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

    def _get_manifest_csv(self, token: str) -> list[bytes]:
        try:
            headers = {AUTHORIZATION: f"Bearer {token}"}
            self.conn.request(OPTIONS, EMPTY_PATH, headers=headers)
            response = self.conn.getresponse()
            if response.status == HTTPStatus.OK:
                return response.readlines()
            else:
                raise RuntimeError(f"Oops, got a {response.status}")
        finally:
            self.conn.close()

