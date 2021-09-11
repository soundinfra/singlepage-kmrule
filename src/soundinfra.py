# This file contains all the code, constants, and other information required
# to communicate with the Sound//Infra API.
import hashlib
import logging
import os
from http.client import HTTPSConnection, HTTPResponse
from http import HTTPStatus
from os.path import relpath
from pathlib import Path

from src.standards import validate_domain_name, pretty_status, pretty_code
from src.types import FileSet, Method

AUTHORIZATION = "Authorization"
COMMA = ","
SLASH = "/"
GLOB_ALL = "*"
HTTPS = "https"
READ_BINARY = "rb"
SUCCESS = HTTPStatus.OK
TOKEN_MAX_LENGTH = 100
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


def parse_line(index: int, line: bytes, separator=COMMA) -> tuple[str, str]:
    try:
        values = line.decode(UTF8).strip().split(separator)
        if len(values) < 2:
            raise ValueError(
                f"Error: Expected two columns on line {index} of CSV.")
        filename = values[1].strip()
        hash = values[0].strip()
        if not hash.isalnum():
            raise ValueError(
                f"Error: Hash on line {index} does not look valid.")
        return (filename, hash)
    except UnicodeDecodeError as err:
        raise ValueError(
            f"Error: Decode error on line {index} ({str(err)}).")


def parse_csv(lines: list[bytes], separator=COMMA) -> FileSet:
    result = {}
    for index, line in enumerate(lines, 1):
        filename, hash = parse_line(index, line, separator=separator)
        if filename in result:
            raise ValueError(
                f"Error: Multiple entries for file: {filename}.")
        else:
            result[filename] = hash
    return result


def validate_token(token: str) -> None:
    if not token or type(token) is not str:
        raise ValueError("Accesss token must be a valid, non-empty string.")
    if len(token) > TOKEN_MAX_LENGTH:
        raise ValueError("Access token is too long, should be under "
                         f"{TOKEN_MAX_LENGTH} characters.")
    if not token.isalnum():
        raise ValueError("Access token should contain only alphanumeric "
                         "characters.")


class SoundInfraClient():

    def __init__(self, site: str, token: str, conn: HTTPSConnection = None):
        validate_domain_name(site)
        validate_token(token)
        self.token = token
        if not conn:
            self.conn = HTTPSConnection(site)
        else:
            self.conn = conn

    def __enter__(self):
        self.conn.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.close()

    def _get_base_headers(self):
        return {AUTHORIZATION: f"Bearer {self.token}"}

    def _get_manifest_csv(self) -> list[bytes]:
        response = self._do_request(Method.OPTIONS, SLASH)
        return self._handle_response(response)

    def _do_request(self, method: Method,
                    path=SLASH,
                    body=None) -> HTTPResponse:
        body_bytes = len(body) if body else 0
        logging.debug(f"Making request {method}, {path}. "
                      f"Body is {body_bytes} bytes long.")
        self.conn.request(method.value, path,
                          headers=self._get_base_headers(),
                          body=body)
        return self.conn.getresponse()

    def _handle_response(self, response: HTTPResponse) -> list[bytes]:
        if response.status == SUCCESS:
            lines = response.readlines()
            # For some reason calling readlines() does not close the response.
            response.close()
            return lines
        else:
            raise RuntimeError(f"Expected {pretty_status(SUCCESS)} but got a "
                               f"{pretty_code(response.status)}")

    def get_manifest(self) -> FileSet:
        return parse_csv(self._get_manifest_csv())

    def put(self, directory: str, name: str) -> str:
        local_path = Path(directory).joinpath(Path(name))
        remote_path = SLASH + name
        size = os.path.getsize(local_path)
        logging.info(f"Publishing {local_path} as {remote_path} ({size} "
                     "bytes)")
        with open(local_path, READ_BINARY) as content:
            response = self._do_request(Method.PUT, remote_path,
                                        body=content.read())
            lines = self._handle_response(response)
            parsed = parse_csv(lines, separator=SLASH)
            if len(parsed) == 1:
                return parsed[name]
            else:
                raise RuntimeError(
                    f"Response should be one line! {parsed}.")

    def delete(self, name: str) -> None:
        remote_path = SLASH + name
        response = self._do_request(Method.DELETE, remote_path)
        lines = self._handle_response(response)
        if lines:
            decoded = "\n".join([line.decode(UTF8) for line in lines])
            raise RuntimeError("Response body should be empty, " +
                               f"not: {decoded}.")
