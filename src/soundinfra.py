# This file attempts to capture all the Sound//Infra specific code, parsing
# constants and the like.
import os

FileSet = dict[str, str]

TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"
COMMA = ","
UTF8 = "utf-8"


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


def get_token() -> str:
    if TOKEN_ENV_VAR in os.environ:
        return os.environ[TOKEN_ENV_VAR]
    else:
        raise ValueError(f"SoundInfra token {TOKEN_ENV_VAR} is not set")
