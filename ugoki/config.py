"Reads config from env"

import os
import sys
from pathlib import Path

DEV_MODE = "UGOKI_DEV" in os.environ

if DEV_MODE:
    print("Running in Dev Mode.")
    print("Username: test, Password: test")
    print()
    STORAGE = Path(__file__).absolute().parent / "static"
    SERVE_ROOT = "http://localhost:8000/static"
    AUTH_USER = "test"
    AUTH_PASSWORD = "test"
else:
    try:
        STORAGE = Path(os.environ["UGOKI_STORAGE"]).absolute()
        SERVE_ROOT = os.environ["UGOKI_ROOT"].rstrip("/")
        AUTH_USER = os.environ["UGOKI_USER"]
        AUTH_PASSWORD = os.environ["UGOKI_PASSWORD"]

        if not STORAGE.is_dir() or not os.access(STORAGE, os.W_OK):
            raise ValueError(
                "UGOKI_STORAGE does not point to a writeable directory"
            )
    except KeyError as e:
        print(f"Please set the following environment variable: {e}",
              file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(2)