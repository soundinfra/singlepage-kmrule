#! /usr/local/bin/python3
import os
import hashlib
from pathlib import Path
PUBLISH_DIR = "public"
print(f"Publishing contents of: {PUBLISH_DIR}")
for path in sorted(Path(PUBLISH_DIR).rglob('*')):
    if path.is_file():
        md5 = hashlib.md5()
        md5.update(open(path, 'rb').read())
        print(f"{md5.hexdigest()},{os.path.relpath(path, PUBLISH_DIR)}")


