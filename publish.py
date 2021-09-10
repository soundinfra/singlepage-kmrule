#! /usr/bin/env python3
import logging

from src import publish
import sys

if __name__ == "__main__":
    args = publish.setup(sys.argv[1:])
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Verbose logging enabled.")
    else:
        logging.basicConfig(level=logging.INFO)
    publish.publish(args)
