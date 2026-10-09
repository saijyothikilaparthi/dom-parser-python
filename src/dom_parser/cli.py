import sys
from pathlib import Path

from dom_parser.parser import ParseError, parse
from dom_parser.renderer import render
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


def main(argv: list[str]) -> int:
    args = [arg for arg in argv if arg not in ("--tokens", "--tree")]
    inspect_tokens = "--tokens" in argv
    print_tree = "--tree" in argv

    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 1

    contents = read_file(args[0])
    if contents is None:
        print(f"Cannot open file: {args[0]}", file=sys.stderr)
        return 1

    if print_tree:
        try:
            document = parse(contents)
        except ParseError as error:
            print(error, file=sys.stderr)
            return 1
        sys.stdout.write(render(document))
        return 0

    if inspect_tokens:
        for token in tokenize(contents):
            print(format_token(token))
        return 0

    sys.stdout.write(contents)
    return 0


def run() -> None:
    sys.exit(main(sys.argv[1:]))
