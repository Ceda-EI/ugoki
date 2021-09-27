"CLI interface for ugoki"

import argparse
import os
import uvicorn


def dev():
    "Runs the dev server"
    os.environ["UGOKI_DEV"] = "1"
    uvicorn.run("ugoki.main:app", host="127.0.0.1", port=8000)


def prod():
    "Runs the production server"
    parser = argparse.ArgumentParser()
    parser.add_argument("STORAGE", help="Path to store gifs")
    parser.add_argument(
        "SERVE_ROOT",
        help="Root where the gifs are served by the web server"
    )
    parser.add_argument(
        "AUTH_USER",
        help="Username for API"
    )
    parser.add_argument(
        "AUTH_PASSWORD",
        help="Password for API"
    )
    parser.add_argument(
        "DB_STRING",
        help="String to connect to database. (e.g. sqlite:///ugoki.sqlite)"
    )
    parser.add_argument(
        "-p", "--port",
        default=8000,
        type=int,
        help="Port to listen on. Default: 8000"
    )
    parser.add_argument(
        "-H", "--host",
        default="127.0.0.1",
        help="Host to listen for. Default: 127.0.0.1"
    )
    args = parser.parse_args()
    os.environ["UGOKI_STORAGE"] = args.STORAGE
    os.environ["UGOKI_ROOT"] = args.SERVE_ROOT
    os.environ["UGOKI_USER"] = args.AUTH_USER
    os.environ["UGOKI_PASSWORD"] = args.AUTH_PASSWORD
    os.environ["UGOKI_DB_URL"] = args.DB_STRING

    uvicorn.run("ugoki.main:app", host=args.host, port=args.port)
