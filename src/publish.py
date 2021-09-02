#! /usr/local/bin/python3
from os.path import relpath
import hashlib
from pathlib import Path
import logging

logging.basicConfig(level=logging.WARNING)

PUBLISH_DIR = "public"
GLOB_ALL = "*"
READ_BINARY = "rb"

FileSet = dict[str, str]


def hash_file(path: Path) -> str:
    md5 = hashlib.md5()
    md5.update(open(path, READ_BINARY).read())
    return md5.hexdigest()


def hash_local_files(publish_dir: str) -> FileSet:
    files = [path for path in Path(publish_dir).rglob(GLOB_ALL)
             if path.is_file()]
    return {relpath(path, publish_dir): hash_file(path)
            for path in sorted(files)}


def read_remote_csv(filename: str) -> FileSet:
    result = {}
    for line in open(filename, READ_BINARY).readlines():
        values = line.decode().strip().split(",")
        result[values[1]] = values[0]
    return result


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


# Publishes contents of publish_dir.
# Skips files that have already been published (based on hash).
# Will not delete any files from remote, use clean operation for that.
def publish_site(publish_dir: str, remote_csv: str):
    print(f"Publishing contents of: {publish_dir}")
    local_files = hash_local_files(publish_dir)
    remote_files = read_remote_csv(remote_csv)
    diff = diff_files(local_files, remote_files)
    print(diff)
