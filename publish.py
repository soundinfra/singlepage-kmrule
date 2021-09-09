#! /usr/bin/env python3

import sys

from src import publish

PUBLIC = "public"


if __name__ == "__main__":
    publish.setup(sys.argv[1:])
