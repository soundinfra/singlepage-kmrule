# This file contains types that are used across the project.
from enum import Enum
from typing import NamedTuple

FileSet = dict[str, str]


class Method(Enum):
    GET = "GET"
    PUT = "PUT"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"


class PublishArgs(NamedTuple):
    domain: str
    directory: str
    token: str
    dryrun: bool = True
    clean: bool = False
    verbose: bool = False
