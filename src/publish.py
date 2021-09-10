# This file contains
import os

from src.soundinfra import build_manifest, SoundInfraClient, parse_line
from src.types import FileSet, PublishArgs
import argparse
import logging

PUBLISH_DIR = "public"
TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"


def token_from_env() -> str:
    if TOKEN_ENV_VAR in os.environ:
        return os.environ[TOKEN_ENV_VAR]
    else:
        raise ValueError(f"SoundInfra token {TOKEN_ENV_VAR} is not set.")


def hashes_match(name: str, local: str, remote: str) -> bool:
    if local == remote:
        logging.debug(f"Remote {name} hash ({local}) matches local hash.")
        return True
    else:
        logging.debug(
            f"Hash mismatch for {name} local: {local}, remote: {remote}.")
        return False


# Takes a dict of local files, and a list of (hash, name) tuples for the
# remote files
def diff_files(local_files: FileSet, remote_files: FileSet) -> FileSet:
    result = {}
    for name, hash in local_files.items():
        if name in remote_files:
            if not hashes_match(name, hash, remote_files[name]):
                result[name] = hash
        else:
            logging.info(f"{name} ({hash}) is not published.")
            result[name] = hash
    return result


def clean_files(local_files: FileSet, remote_files: FileSet) -> list[str]:
    return [name for name in remote_files.keys()
            if name not in local_files]


def parse(argv):
    parser = argparse.ArgumentParser(
        description="Publish to the web with Sound//Infra.")
    parser.add_argument("domain", type=str,
                        help="The domain to publish to, like example.com.")
    parser.add_argument("--directory", dest="directory",
                        type=str, default=PUBLISH_DIR,
                        help=f"Directory to publish (default '{PUBLISH_DIR}')")
    parser.add_argument("-v", "--verbose",  action="store_true",
                        help="Enable verbose logging.")
    parser.add_argument("--token", type=str,
                        help="Override Sound//Infra access token. By default,"
                             f"this program will look at the "
                             f"{TOKEN_ENV_VAR} environment variable.")
    parser.add_argument("--clean", action="store_true",
                        help="If true, clean files from the domain.")
    return parser.parse_args(argv)


def setup(argv):
    args = parse(argv)
    return PublishArgs(domain=args.domain, directory=args.directory,
                       clean=args.clean,
                       verbose=args.verbose,
                       token=args.token if args.token else token_from_env())


# Publishes contents of publish_dir.
# Skips files that have already been published (based on hash).
# Will not delete any files from remote, use clean operation for that.
def publish(args: PublishArgs):
    logging.info(f"Publishing contents of '{args.directory}' to "
                 f"'{args.domain}'.")
    client = SoundInfraClient(args.domain, args.token)
    local_files = build_manifest(args.directory)
    remote_files = client.get_manifest()
    diff = diff_files(local_files, remote_files)
    logging.info(f"Publish diff summary: ({len(local_files)},"
                 f" {len(remote_files)}, {len(diff)}) (local, remote, "
                   "updated) files.")
    for name, hash in diff.items():
        logging.debug(f"Publishing: {name} ({hash[:5]}...)")
        returned_hash = client.put(args.directory, name)
        if hashes_match(name, hash, returned_hash):
            logging.debug(f"Successfully published {name}.")
        else:
            logging.warning(f"Failed hash mismatch for {name}!!! "
                            f"(local {hash}, returned: {returned_hash}).")
