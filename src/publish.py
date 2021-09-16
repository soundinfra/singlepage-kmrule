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
        token = os.environ[TOKEN_ENV_VAR]
        if token:
            return token
        else:
            raise ValueError(
                f"SoundInfra token {TOKEN_ENV_VAR} is not a valid string.")
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
    parser.add_argument("--dryrun", action="store_true",
                        default=False,
                        help="Simulate, but don't actually publish files.")
    parser.add_argument("--clean", action="store_true",
                        help="If true, clean files from the domain.")
    return parser.parse_args(argv)


def setup(argv):
    args = parse(argv)
    return PublishArgs(domain=args.domain, directory=args.directory,
                       clean=args.clean,
                       verbose=args.verbose,
                       dryrun=args.dryrun,
                       token=args.token if args.token else token_from_env())


def verify_clean(file_count: int, domain: str):
    logging.warning(
        f"About to clean {file_count} files from {domain}.")
    answer = input(
        "Are you sure you want to continue? y/N yes/NO\n").lower()
    if answer == 'y' or answer == "yes":
        logging.warning(
            f"OK, cleaning {file_count} files from {domain}.")
        return True
    else:
        logging.warning("Cleaning canceled. No worries, have a nice day!")
        return False


def do_clean(client: SoundInfraClient, args: PublishArgs, diff: list[str]):
    for name in diff:
        logging.warning(f"Deleting {name} from {args.domain}.")
        if args.dryrun:
            logging.info(f"[dryrun] Deleted {name}.")
        else:
            client.delete(name)
            logging.info(f"Deleted {name} from {args.domain}.")


def clean(args: PublishArgs):
    logging.warning(f"Cleaning {args.domain} based on contents of "
                    f"'{args.directory}.")
    with SoundInfraClient(args.domain, args.token) as client:
        local_files = build_manifest(args.directory)
        remote_files = client.get_manifest()
        diff = clean_files(local_files, remote_files)
        if verify_clean(len(diff), args.domain):
            do_clean(client, args, diff)


def publish_file(client: SoundInfraClient,
                 name: str,
                 directory: str,
                 hash: str):
    returned_hash = client.put(directory, name)
    if hashes_match(name, hash, returned_hash):
        logging.debug(f"Successfully published {name}.")
    else:
        raise RuntimeError(
            f"Aborting due to failed hash mismatch for '{name}'!!! (local"
            f" '{hash}', returned: '{returned_hash}').")


def do_publish(client: SoundInfraClient, args: PublishArgs, diff: FileSet):
    for name, hash in diff.items():
        logging.debug(f"Publishing: {name} ({hash[:5]}...)")
        if args.dryrun:
            logging.debug(f"[Dryrun] Published {name}.")
        else:
            publish_file(client, name, args.directory, hash)


# Publishes contents of publish_dir.
# Skips files that have already been published (based on hash).
# Will not delete any files from remote, use clean operation for that.
def publish(args: PublishArgs):
    logging.info(f"Publishing contents of '{args.directory}' to "
                 f"'{args.domain}'.")
    with SoundInfraClient(args.domain, args.token) as client:
        local_files = build_manifest(args.directory)
        remote_files = client.get_manifest()
        diff = diff_files(local_files, remote_files)
        logging.info(f"Publish diff summary: ({len(local_files)},"
                     f" {len(remote_files)}, {len(diff)}) (local, remote, "
                     "updated) files.")
        do_publish(client, args, diff)
