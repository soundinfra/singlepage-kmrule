# This file contains code relating to standards that are outside
# the control of Sound//Infra, mostly web standards (HTTP etc).
from http import HTTPStatus

DOMAIN_MAX_LENGTH = 253
DOT = "."


def pretty_status(status: HTTPStatus) -> str:
    return f"HTTP {status.value} ({status.name})"


def pretty_code(code: int) -> str:
    return pretty_status(HTTPStatus(code))


def validate_domain_name(name: str) -> None:
    if not name:
        raise ValueError("Domain name cannot be blank.")
    if len(name) > DOMAIN_MAX_LENGTH:
        raise ValueError(f"Domain name is too long ({len(name)} chars, " +
                         f"max is {DOMAIN_MAX_LENGTH}).")
    if DOT not in name:
        raise ValueError(f"No Top-Level-Domain found in: \"{name}\".")
    # Check domain name for (incomplete) list of invalid characters.
    for char in name:
        if char in "_!@#$%^&*":
            raise ValueError(f"Invalid character {char} in domain name.")
