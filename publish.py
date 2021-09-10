#! /usr/bin/env python3
import logging

from src import publish
import sys

logging.basicConfig(level=logging.WARNING)

if __name__ == "__main__":
    args = publish.setup(sys.argv[1:])
    publish.publish(args)
