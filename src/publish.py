# This file contains
import os

from src.soundinfra import build_manifest, SoundInfraClient
from src.types import FileSet, PublishArgs
import argparse
import logging

PUBLISH_DIR = "public"
TOKEN_ENV_VAR = "SOUNDINFRA_TOKEN"


def token_from_env() -> str:
    if TOKEN_ENV_VAR in os.environ:
        return os.environ[TOKEN_ENV_VAR]
    else:
        raise ValueError(f"SoundInfra token {TOKEN_ENV_VAR} is not set")


def hashes_match(name, local, remote):
    if local is remote:
        logging.info(f"Remote {name} hash ({local}) matches local hash")
        return True
    else:
        logging.info(
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
                       token=args.token if args.token else token_from_env())


# Publishes contents of publish_dir.
# Skips files that have already been published (based on hash).
# Will not delete any files from remote, use clean operation for that.
def publish(args: PublishArgs):
    print(f"Publishing contents of: {args.directory} at: ")
    local_files = build_manifest(args.directory)
    client = SoundInfraClient(args.domain)
    remote_files = client.get_remote_fileset(args.token)
    diff = diff_files(local_files, remote_files)
    print(diff)
