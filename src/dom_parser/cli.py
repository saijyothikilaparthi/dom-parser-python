import sys
from pathlib import Path

USAGE = (
    "Usage: domparser FILE [--tree | --text | --find-tag TAG "
    "| --find-id ID | --find-class CLASS]"
)


def read_file(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 1

    contents = read_file(argv[0])
    if contents is None:
        print(f"Cannot open file: {argv[0]}", file=sys.stderr)
        return 1

    sys.stdout.write(contents)
    return 0


def run() -> None:
    sys.exit(main(sys.argv[1:]))
