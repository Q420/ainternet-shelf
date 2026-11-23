"""Process entry: `python3 -m checker` — one JSON request on
stdin, one JSON verdict on stdout (Piece 7, §3.10)."""
import sys

from checker.checker import main

if __name__ == "__main__":
    sys.exit(main())
