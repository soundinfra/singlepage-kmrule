# This file contains types that are used across the project.
from typing import NamedTuple


class PublishArgs(NamedTuple):
    domain: str
    directory: str
    token: str
    dryrun: bool = True
    clean: bool = False
    verbose: bool = False


FileSet = dict[str, str]
