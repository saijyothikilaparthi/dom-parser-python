import sys
from pathlib import Path

from dom_parser.nodes import Document
from dom_parser.parser import ParseError, parse
from dom_parser.query import find_by_class, find_by_id, find_by_tag
from dom_parser.renderer import render, render_text
from dom_parser.tokenizer import tokenize
from dom_parser.tokens import EndTag, StartTag, Token

USAGE = (
    "Usage: domparser FILE [--tree | --text | --find-tag TAG "
    "| --find-id ID | --find-class CLASS]"
)


def read_file(path: str) -> str | None:
    try:
        with Path(path).open(encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def format_token(token: Token) -> str:
    if isinstance(token, StartTag):
        return f"OPEN {token.name}"
    if isinstance(token, EndTag):
        return f"CLOSE {token.name}"
    return f"TEXT {token.content!r}"


def parse_args(argv: list[str]) -> tuple[str | None, str | None, bool, list[str]] | None:
    mode: str | None = None
    query_value: str | None = None
    inspect_tokens = False
    files: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--tokens":
            inspect_tokens = True
        elif arg in ("--tree", "--text"):
            mode = arg[2:]
        elif arg in ("--find-tag", "--find-id", "--find-class"):
            if i + 1 >= len(argv):
                return None
            mode = arg[2:]
            query_value = argv[i + 1]
            i += 1
        elif arg.startswith("-"):
            return None
        else:
            files.append(arg)
        i += 1
    return mode, query_value, inspect_tokens, files


def main(argv: list[str]) -> int:
    parsed = parse_args(argv)
    if parsed is None or len(parsed[3]) != 1 or parsed[3][0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 1

    mode, query_value, inspect_tokens, files = parsed
    path = files[0]

    contents = read_file(path)
    if contents is None:
        print(f"Cannot open file: {path}", file=sys.stderr)
        return 1

    if mode is None and inspect_tokens:
        for token in tokenize(contents):
            print(format_token(token))
        return 0

    if mode is None:
        sys.stdout.write(contents)
        return 0

    try:
        document = parse(contents)
    except ParseError as error:
        print(error, file=sys.stderr)
        return 1

    if mode == "tree":
        sys.stdout.write(render(document))
        return 0

    if mode == "text":
        sys.stdout.write(render_text(document))
        return 0

    if mode == "find-tag":
        matches = find_by_tag(document, query_value or "")
    elif mode == "find-id":
        matches = find_by_id(document, query_value or "")
    else:
        matches = find_by_class(document, query_value or "")

    if matches:
        sys.stdout.write(render(Document(children=list(matches))))
    return 0


def run() -> None:
    sys.exit(main(sys.argv[1:]))
