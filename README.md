# dom-parser-python

A small command-line parser for a deliberately tiny subset of HTML. It reads an
HTML file, tokenizes it, builds an in-memory DOM, prints the tree, validates tag
nesting, and answers a few simple queries. Standard library only at runtime.

## Supported features

- Read one HTML file path and print its contents unchanged (LF and CRLF line
  endings and the presence/absence of a final newline are preserved).
- Empty and text-only files are valid input.
- Tokenizer for opening tags, closing tags, and text, in source order.
- DOM with elements and text nodes, supporting nested elements, siblings, text
  before/between/after tags, multiple top-level elements, and empty documents.
- Double-quoted attributes (`name="value"`) stored on elements in source order,
  including empty values.
- Recursive tree printing (`.`, `├──`, `└──`, `│`), with text nodes in double
  quotes and attributes as `[name="value", ...]`.
- Nesting validation: unexpected closing tags, wrong nesting, and unclosed tags.
- Queries: `--text`, `--find-tag TAG`, `--find-id ID`, `--find-class CLASS`.
- Temporary token inspection via `--tokens`.

## Limitations (out of scope)

- No comments, DOCTYPE, JavaScript, or CSS.
- No HTML entities.
- No void/self-closing tags; every element must have an explicit closing tag.
- Only double-quoted attribute values; single-quoted and unquoted values are
  ignored.
- No CSS selector syntax; only the four documented query options.
- No line/column numbers in error messages.

## Requirements

- Python 3.12+

## Setup

Using [uv](https://docs.astral.sh/uv/):

```sh
uv venv
uv pip install -e ".[dev]"
```

Using pip:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

This installs the `domparser` console script and the development tools
(`pytest`, `ruff`, `mypy`).

## Usage

```sh
domparser FILE                     # print the file contents unchanged
domparser FILE --tree              # print the DOM as an indented tree
domparser FILE --text              # print non-whitespace text nodes, one per line
domparser FILE --find-tag TAG      # print subtrees of elements with that tag
domparser FILE --find-id ID        # print subtrees of elements with that id
domparser FILE --find-class CLASS  # print subtrees of elements with that class token
domparser FILE --tokens            # temporary: print the token stream
```

`domparser` can also be run as a module: `python -m dom_parser FILE ...`

### Examples

Given `samples/page.html`:

```sh
$ domparser samples/page.html --tree
.
└── html
    ├── head
    │   └── title
    │       └── "Sample"
    └── body
        ├── h1 [id="top", class="title"]
        │   └── "Welcome"
        ├── p [class="intro"]
        │   ├── "Hello "
        │   └── b
        │       └── "world"
        └── ul [class="list"]
            ├── li [class="item"]
            │   └── "One"
            └── li [class="item"]
                └── "Two"

$ domparser samples/page.html --find-class item
.
├── li [class="item"]
│   └── "One"
└── li [class="item"]
    └── "Two"

$ domparser samples/attributes.html --text
Hi
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | File could not be opened, invalid arguments, or invalid HTML |

Invalid arguments print:

```
Usage: domparser FILE [--tree | --text | --find-tag TAG | --find-id ID | --find-class CLASS]
```

A file-open failure prints `Cannot open file: FILE`. Validation failures print
`Unexpected closing tag: </x>`, `Unexpected closing tag: </x> (expected </y>)`,
or `Unclosed tag: <x>`. All errors go to stderr.

## Testing

One command runs the whole test suite:

```sh
uv run pytest
```

Or with an activated virtual environment: `python -m pytest`.

Static checks:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Tests live under `tests/`:

- `test_tokenizer.py` – token kinds, order, whitespace, attributes.
- `test_parser.py` – DOM shape, nesting, siblings, text placement, attributes.
- `test_renderer.py` – exact tree output.
- `test_validate.py` – exact validation error messages.
- `test_query.py` – query behavior.
- `test_cli.py` – CLI argument handling, exit codes, error output.
- `test_golden.py` – end-to-end golden-file comparisons for all cases.

Fixtures are in `tests/fixtures/` and expected outputs in `tests/golden/`, and
cover simple, nested, attributes, siblings, empty, deep, text-only, and page
documents plus the unclosed, unexpected-close, and wrong-nesting error cases.

## Project layout

```
src/dom_parser/
  __main__.py   # python -m dom_parser
  cli.py        # argument handling and entry point
  tokens.py     # token dataclasses
  tokenizer.py  # text -> tokens
  nodes.py      # DOM node dataclasses
  parser.py     # tokens -> DOM, with validation
  renderer.py   # tree and text rendering
  query.py      # tag/id/class lookups
tests/          # pytest suite, fixtures/, golden/
samples/        # manual sample HTML files
plan.md         # phase-by-phase development plan
```

## Git history vs. Entire context

This repository uses two complementary records of its development:

- **Git history** is the source of truth for *what changed*. It holds the
  committed snapshots and messages (currently one commit per phase, from
  "created python parser development plan" through "Implement Phase 7 HTML query
  options"). Untracked working-tree files — such as the Phase 8 fixtures and
  golden outputs — are not yet part of history until committed.

- **Entire** captures the *context around* the changes. It is enabled in
  `.entire/settings.json` (`checkpoints.primary.type = "git-refs"`) with the
  OpenCode plugin, so as work proceeds it records session metadata (prompts,
  logs) under `.entire/` and creates git-ref checkpoints aligned with commits.
  Its own ignore rules (`.entire/.gitignore`) keep local artifacts like `tmp/`,
  `logs/`, and `metadata/` out of Git.

In short: Git answers "what does the code look like and how did it change",
while Entire answers "how and why was it developed, and how do I return to a
known-good state" — the two are used together rather than as substitutes.
