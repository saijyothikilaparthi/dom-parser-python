# Development Plan: dom-parser-python

A Python command-line program that reads a small subset of HTML, builds a DOM tree in memory, and prints the tree.

## In scope

- Opening tags, closing tags, text
- Nested elements and sibling elements
- Double-quoted attributes (`<div id="main">`)
- Whitespace between elements

## Out of scope (optional extensions only, not required)

- Comments, JavaScript, CSS
- HTML entities, DOCTYPE
- Self-closing / void tags
- Single-quoted or unquoted attribute values
- CSS selector syntax

---

## Phase 1: Read the HTML file

**Goal:** Load raw HTML text from a file path given on the command line.

**What needs to be understood:**
- Python file I/O (`pathlib.Path.read_text`, encoding)
- Command-line argument handling (`argparse`)
- Error cases: missing file, unreadable file

**What will be implemented:**
- A `main()` entry point accepting a file path argument
- A function that reads the file and returns its contents as a string
- A clear error message and non-zero exit code for bad input

**How it will be tested:**
- Unit tests with temporary files (valid content, missing file)
- Manual run: `python -m dom_parser sample.html`

**Completion condition:** The program returns the exact file content for a valid HTML file and exits with a non-zero status plus a readable message for bad input.

---

## Phase 2: Tokenize the HTML

**Goal:** Convert the raw HTML string into a flat sequence of tokens.

**What needs to be understood:**
- Token kinds needed: start tag, end tag, text
- Tokenizer states: outside a tag, inside a tag, inside a double-quoted attribute value
- Whitespace between elements (decide: preserve text nodes as-is or skip whitespace-only text)

**What will be implemented:**
- Token data structures (start tag with tag name + attributes, end tag, text)
- A tokenizer function: `str -> list[Token]`
- Parsing of double-quoted attributes at this stage (details land in Phase 5)

**How it will be tested:**
- Table-driven tests: input string → expected token list
- Cases: plain text, one element, nested elements, siblings, whitespace between elements, double-quoted attributes

**Completion condition:** Every in-scope HTML snippet produces the exact expected token list.

---

## Phase 3: Design and build the DOM

**Goal:** Turn the token stream into an in-memory tree of nodes.

**What needs to be understood:**
- The required HTML constructs: nesting, siblings, text
- Tree building with a stack of open elements
- The node model is deliberately left open — decide node types and fields here based on what Phases 4–7 actually need (no assumptions made in this plan)

**What will be implemented:**
- Node representation (to be designed in this phase)
- A tree builder: `list[Token] -> tree` using an open-element stack
- A parser entry point: `parse(html: str) -> tree`

**How it will be tested:**
- Unit tests asserting tree shape: depth, child order, tag names
- Nesting cases (`<a><b>x</b></a>`) and sibling cases (`<a></a><a></a>`)

**Completion condition:** Parsing representative in-scope snippets yields the correct tree structure, verified by tests.

---

## Phase 4: Print the DOM tree

**Goal:** Render the tree to stdout in a readable, indented format.

**What needs to be understood:**
- Tree traversal (recursive pre-order walk over whatever node model Phase 3 chose)
- Indentation (e.g. 2 spaces per depth level)
- Output line format for elements and text

**What will be implemented:**
- A render function producing an indented listing, e.g.:
  - `html`
    - `body`
      - `p`
        - `Hello`

**How it will be tested:**
- Golden-output tests: capture stdout and compare to an expected multiline string
- Manual visual check on a sample HTML file

**Completion condition:** `python -m dom_parser sample.html` prints an indented tree matching the expected output exactly.

---

## Phase 5: Parse and store attributes

**Goal:** Capture double-quoted attributes from opening tags and expose them on element nodes.

**What needs to be understood:**
- Only the required form: `name="value"` (double quotes only)
- Where attributes live in the token model and on the DOM node
- Storage shape (e.g. a name → value mapping on each element)

**What will be implemented:**
- Attribute parsing for `name="value"` pairs inside start-tag tokens
- Storage of attributes on element nodes
- Renderer update so attributes appear in the printed tree

**How it will be tested:**
- Tokenizer tests: one attribute, several attributes, whitespace inside the tag
- Tree/renderer tests confirming attributes are shown in output
- Out-of-scope forms (single quotes, unquoted) are not supported and need no tests

**Completion condition:** Double-quoted attributes are parsed, stored on elements, and visible in the printed tree.

---

## Phase 6: Validate malformed HTML

**Goal:** Detect and report exactly three malformation cases with the exact required messages.

**What needs to be understood:**
- The three required cases and their message formats (below)
- Validation happens during tree building (open-element stack already gives the needed information)
- Failure behavior: print the message, exit non-zero

**What will be implemented:**

| Case | Meaning | Required message |
|---|---|---|
| Unexpected closing tag | Closing tag with no matching open element | `Unexpected closing tag: </section>` |
| Wrong nesting | Closing tag does not match the innermost open element | `Unexpected closing tag: </b> (expected </i>)` |
| Unclosed tag | End of input with elements still open | `Unclosed tag: <div>` |

- Validation checks in the tree builder
- Message construction with the exact wording and tag names shown above
- Non-zero exit code on any validation failure

**How it will be tested:**
- One test per case asserting the exact message string
- Valid fixtures must produce no errors (no false positives)
- CLI-level test asserting the message on stderr/stdout and the exit code
- No line/column reporting — messages contain only what the required format shows

**Completion condition:** Each of the three cases produces its exact required message, valid HTML produces no errors, and the CLI exits non-zero on failure.

---

## Phase 7: Implement queries

**Goal:** Let users query the parsed DOM from the command line with exactly four flags.

**What needs to be understood:**
- The four required flags and what each returns
- A simple tree walk is enough — no selector language, no selector parser

**What will be implemented — exactly these flags:**

| Flag | Behavior |
|---|---|
| `--text` | Print the text content |
| `--find-tag TAG` | Find elements with the given tag name |
| `--find-id ID` | Find elements with the given `id` attribute |
| `--find-class CLASS` | Find elements with the given `class` attribute |

- Lookup functions over the tree for tag name, `id`, and `class`
- CLI wiring: `python -m dom_parser sample.html --find-tag div`

Nothing beyond these four flags. No CSS selectors, no combinators, no attribute-value operators.

**How it will be tested:**
- One test per flag against a fixed fixture tree
- No-match case returns empty output with success exit code
- CLI tests for argument handling and output format

**Completion condition:** All four flags return the correct elements on fixtures and print them.

---

## Phase 8: Add automated tests and refactor

**Goal:** Consolidate test coverage and clean up the codebase.

**What needs to be understood:**
- Current gaps: integration/CLI paths, error paths, edge cases
- Duplication or unclear responsibilities accumulated across phases

**What will be implemented:**
- End-to-end tests: file in → printed tree / query output / validation message out
- Fixture files for realistic HTML samples (valid and malformed)
- Refactoring into clear modules (tokenizer, tree builder, renderer, validation, queries, CLI)

**How it will be tested:**
- Full suite run; review untested branches
- Re-run all earlier golden-output and error-message tests after refactoring to confirm no behavior change

**Completion condition:** One command runs the whole suite green, all phases and error paths are covered, and the code has no duplicated logic.

---

## Python Project Structure

```
dom-parser-p/
├── plan.md
├── README.md
├── pyproject.toml          # project metadata, entry point
├── src/
│   └── dom_parser/
│       ├── __init__.py
│       ├── __main__.py     # python -m dom_parser
│       ├── cli.py          # argparse / main()
│       ├── tokenizer.py    # Phase 2 + Phase 5 attributes
│       ├── tokens.py       # token structures
│       ├── nodes.py        # DOM node model (designed in Phase 3)
│       ├── parser.py       # tokens -> tree + Phase 6 validation
│       ├── renderer.py     # Phase 4 printing
│       └── query.py        # Phase 7 lookups
├── tests/
│   ├── fixtures/           # sample .html files (valid + malformed)
│   ├── test_tokenizer.py
│   ├── test_parser.py
│   ├── test_renderer.py
│   ├── test_validate.py
│   ├── test_query.py
│   └── test_cli.py         # end-to-end
└── samples/
    └── sample.html         # manual testing input
```

Notes:
- `src/` layout so tests import the installed package, not the source tree by accident.
- Standard library only where possible (`argparse`, `dataclasses`, `pathlib`).
- One module per responsibility, matching the phase order. Node model details are decided in Phase 3.

---

## Testing strategy

- **Framework:** `pytest`, tests in `tests/`, discovered by convention.
- **Layers:**
  1. **Unit tests** — tokenizer, tree builder, renderer, validation, query functions with small inline inputs.
  2. **Golden/output tests** — rendered tree output compared to expected multiline strings.
  3. **Integration/CLI tests** — call `main()` with fixture files; assert output and exit code.
- **Fixtures:** small HTML files per scenario; add a fixture + failing test first when a bug is found.
- **Style:** table-driven where practical; one behavior per test with a descriptive name.
- **Gate:** suite must be green before every commit; each phase lands with its tests.

---

## Git commit strategy

- **Granularity:** one commit per meaningful step — a phase (or a slice) plus its tests. No big-bang commits.
- **Order:** only commit when the suite is green.
- **Messages:** short, imperative summary referencing the phase, e.g. `Add tokenizer for tags, text, and double-quoted attributes`.
- **Workflow:** review with `git status` / `git diff`; stage only intended files (never `.entire/`, `.opencode/`, logs). Keep refactors (Phase 8) in separate commits from behavior changes.

---

## OpenCode usage

- Keep `plan.md` as the source of truth; ask OpenCode to update it when scope changes.
- Implement **one phase at a time** — e.g. "implement Phase 2 following plan.md" — not the whole program at once.
- Ask for tests with each phase, then run `pytest` to verify.
- Use OpenCode to explain code, review `git diff`, and suggest refactors in Phase 8.
- State constraints explicitly in prompts (e.g. "no CSS selectors, only double-quoted attributes") and verify only intended files changed.

---

## Entire usage

- Entire is enabled for this repository (`.entire/settings.json` has `"enabled": true`, with checkpoints of type `git-refs`).
- The Entire OpenCode plugin is installed (`.opencode/plugins/entire.ts`, generated by `entire enable --agent opencode`), so it is active during development from the first commit onward.
- Entire captures development context and checkpoints associated with Git commits, giving known-good states to return to between phases.
- Inspect what Entire records during development: session data under `.entire/` (e.g. `logs/`, `tmp/`) and the git-ref checkpoints it creates alongside commits.
- What belongs in a commit is governed by the repository's git configuration; Entire ships its own ignore rules in `.entire/.gitignore` for its local artifacts (`tmp/`, `logs/`, `metadata/`, `settings.local.json`, `redactors/local/`) — check the actual setup rather than assuming.
