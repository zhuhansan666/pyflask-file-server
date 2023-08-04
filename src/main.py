from htmls import CLI_HELP
from app import scan_dirs, create_pages

import os
import sys
from typing import Any
from flask import Flask
from threading import Thread

def get_value(args: list[str], value_name: str, default: Any=None, prefix: str='--', sep: str='=', match_case: bool=False):
    for argv in args:
        if match_case:
            if argv.startswith(prefix + value_name + sep):
                result = argv.split(sep, 1)[1]
                return result if result else default
        else:
            if argv.lower().startswith(prefix.lower() + value_name.lower() + sep.lower()):
                result = argv.split(sep, 1)[1]
                return result if result else default

    return default

def in_value(args: list[str], value_name: str, default: bool=False, prefix: str='--', match_case: bool=False) -> bool:
    for argv in args:
        if match_case:
            if argv.startswith(prefix + value_name):
                return True
        else:
            if argv.lower().startswith(prefix.lower() + value_name.lower()):
                return True

    return default

args = sys.argv[1:]

PORT = get_value(args, 'port')
HOST = get_value(args, 'host', default='0.0.0.0')
WATCH_DIR = get_value(args, 'watch-dir') or get_value(args, 'watchdir') or os.getcwd()

DEBUG = in_value(args, 'debug')
RECURSION = not (in_value(args, 'no-recursion') or in_value(args, 'norecursion'))
HELP = in_value(args, 'help')

if __name__ == '__main__':
    if HELP:
        print(CLI_HELP)
        sys.exit(0)

    app = Flask(__name__)
    create_pages(app, scan_dirs(WATCH_DIR, RECURSION))

    app.run(host=HOST, port=PORT, debug=DEBUG)
