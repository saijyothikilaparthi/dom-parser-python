# Development Plan: dom-parser-python

A Python command-line program that reads a small subset of HTML, builds a DOM tree in memory, and prints the tree.

---

## Phase 1: Read the HTML file

**Goal:** Load raw HTML text from a file path given on the command line.

**What needs to be understood:**
- Python file I/O (`pathlib.Path.read_text`, encoding handling)
- Command-line argument parsing (`argparse` or `sys.argv`)
- Error cases: missing file, unreadable file, empty file

**What will be implemented:**
- A `main()` entry point that accepts a file path argument
- A function that reads the file and returns its contents as a string
- Clear error messages for bad paths / empty input

**How it will be tested:**
- Unit tests with temporary files (valid content, empty file, missing file)
- Manual run: `python -m dom_parser sample.html`

**Completion condition:** The program prints (or returns) the exact file content for a valid HTML file and exits with a non-zero status plus a readable message for bad input.

---

## Phase 2: Tokenize the HTML

**Goal:** Convert the raw HTML string into a flat sequence of tokens.

**What needs to be understood:**
- The supported subset: start tags, end tags, text nodes, comments (decide scope up front)
- Tokenizer states: outside a tag, inside a tag, inside attribute values
- Edge cases: `<` in text, unterminated tags, self-closing `/>`, newlines and whitespace

**What will be implemented:**
- Token types (e.g. `StartTag`, `EndTag`, `Text`, and optionally `Comment`)
- A tokenizer function: `str -> list[Token]`
- Position information (line/column) on tokens for good error messages later

**How it will be tested:**
- Table-driven unit tests: input string → expected token list
- Edge-case tests: empty string, only text, nested-looking tags, malformed tag
- Round-trip sanity check: concatenating text tokens reproduces the input text

**Completion condition:** Every supported HTML snippet produces the exact expected token list, and unsupported/malformed input raises a clear, positioned error or is explicitly defined behavior.

---

## Phase 3: Design and build the DOM

**Goal:** Turn the token stream into an in-memory tree of nodes.

**What needs to be understood:**
- DOM node kinds: element, text (and document root)
- Parent/child relationships and tree invariants
- How to handle mismatched end tags (even if only "best effort" at this stage)

**What will be implemented:**
- Node classes (`Element`, `Text`, `Document`) with `children` (and later `parent`)
- A tree-builder: `list[Token] -> Document` using a stack of open elements
- A small parser entry point: `parse(html: str) -> Document`

**How it will be tested:**
- Unit tests asserting tree shape (depth, child counts, tag names)
- Tests for nesting: `<a><b>x</b></a>` builds the expected hierarchy
- Tests for mismatched tags: defined recovery behavior is verified

**Completion condition:** Parsing representative HTML snippets yields the correct tree structure, verified by tests.

---

## Phase 4: Print the DOM tree

**Goal:** Render the tree to stdout in a readable, indented format.

**What needs to be understood:**
- Tree traversal (recursive pre-order walk)
- Indentation strategy (e.g. 2 spaces per depth level)
- Output format choice: tag lines, text lines, optional attributes placeholder

**What will be implemented:**
- A `render`/`print_tree(node, indent)` function producing lines like:
  - `html`
    - `body`
      - `p`
        - `"Hello"`

**How it will be tested:**
- Golden-output tests: capture stdout (`capsys`) and compare to expected multiline string
- Manual visual check on a sample HTML file

**Completion condition:** `python -m dom_parser sample.html` prints an indented tree that matches the expected output exactly in tests.

---

## Phase 5: Parse and store attributes

**Goal:** Capture attributes from start tags and expose them on element nodes.

**What needs to be understood:**
- Attribute syntax: bare attributes, `key="value"`, `key='value'`, `key=value`, spacing variations
- Where attributes belong in the token and node models

**What will be implemented:**
- Attribute parsing inside the tokenizer (producing `dict[str, str]` on `StartTag`)
- Storage on `Element` nodes (e.g. `element.attributes`)
- Renderer update to display attributes, e.g. `a href="https://example.com"`

**How it will be tested:**
- Tokenizer tests for each attribute form and quoting style
- Tree/renderer tests confirming attributes appear in output
- Duplicate-attribute behavior test (documented decision: first wins or last wins)

**Completion condition:** Attributes are parsed, stored on nodes, and shown in the printed tree, with all attribute-syntax tests passing.

---

## Phase 6: Validate malformed HTML

**Goal:** Detect and report common HTML mistakes instead of silently producing a wrong tree.

**What needs to be understood:**
- Classes of malformation in the supported subset: unclosed tags, stray end tags, tag soup nesting, invalid attribute syntax, mismatched quoting
- Error reporting design: collect-and-report vs. fail-fast
- How strict to be (this is a subset parser, not a full HTML5 conforming parser)

**What will be implemented:**
- Validation checks in the tokenizer and tree builder
- Structured error objects (message, line, column) and a non-zero exit code
- A summary report printed to stderr

**How it will be tested:**
- Corpus of malformed fixtures, each expecting a specific error (or set of errors)
- Valid fixtures must produce zero errors (no false positives)
- Exit-code checks in CLI-level tests

**Completion condition:** Each documented malformation class is detected with an accurate position, valid HTML reports no errors, and the CLI exits non-zero on validation failure.

---

## Phase 7: Implement queries

**Goal:** Let users ask questions of the parsed DOM from the CLI.

**What needs to be understood:**
- Which query forms are in scope for a subset parser (recommended: tag name, `tag[attribute]`, `tag[attribute=value]`, and simple descendant combos)
- Traversal needed to answer queries (recursive walk)
- CLI design: a `--query` flag or a subcommand

**What will be implemented:**
- `find_all(root, selector) -> list[Element]` style API with a small selector parser
- CLI wiring so `python -m dom_parser sample.html --query "a[href]"` prints matches
- Output format for matches (tag + key attributes, or the rendered subtree)

**How it will be tested:**
- Unit tests per query form against a fixed fixture tree
- Tests for no-match results (empty output, success exit code)
- CLI tests for argument handling and output format

**Completion condition:** All documented query forms return the correct elements on fixtures, and the CLI prints them.

---

## Phase 8: Add automated tests and refactor

**Goal:** Consolidate test coverage and clean up the codebase.

**What needs to be understood:**
- Current test gaps (integration/CLI paths, error paths, edge cases)
- Code duplication and unclear responsibilities accumulated across phases

**What will be implemented:**
- End-to-end tests: file in → printed tree/query output out
- Fixture files for realistic HTML samples (valid and malformed)
- Refactoring: clear module boundaries (tokenizer, tree builder, renderer, queries, CLI)
- Optional: lint/format configuration and a single command to run everything

**How it will be tested:**
- Full test suite run; coverage review of untested branches
- Re-run all earlier golden-output and error tests after refactoring to confirm no behavior change

**Completion condition:** One command runs the whole suite green, coverage includes all phases and error paths, and the code is organized with no duplicated logic.

---

## Python Project Structure

```
dom-parser-p/
├── plan.md
├── README.md
├── pyproject.toml          # project metadata, deps, entry point
├── src/
│   └── dom_parser/
│       ├── __init__.py
│       ├── __main__.py     # python -m dom_parser
│       ├── cli.py          # argparse / main()
│       ├── tokenizer.py    # Phase 2 + Phase 5 attributes
│       ├── tokens.py       # token dataclasses
│       ├── nodes.py        # Phase 3 DOM node classes
│       ├── parser.py       # tokens -> tree
│       ├── renderer.py     # Phase 4 printing
│       ├── validate.py     # Phase 6 checks
│       └── query.py        # Phase 7 selectors
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
- Use `src/` layout so tests import the installed package, not the source tree by accident.
- Standard library only where possible (`argparse`, `dataclasses`, `pathlib`); add third-party deps only with a clear reason.
- One module per responsibility, matching the phase order above.

---

## Testing strategy

- **Framework:** `pytest` with tests in `tests/`, discovered by convention.
- **Layers:**
  1. **Unit tests** — tokenizer, tree builder, renderer, query functions in isolation with small inline inputs.
  2. **Golden/output tests** — compare rendered output to expected multiline strings (or `.txt` files in `fixtures/`).
  3. **Integration/CLI tests** — invoke `main()` (or a subprocess) with fixture files and assert stdout, stderr, and exit code.
- **Fixtures:** keep small HTML files for each scenario; add a new fixture whenever a bug is found (regression test first).
- **Style:** table-driven where practical (list of input/expected pairs); one behavior per test with a descriptive name.
- **Gate:** tests must pass before every commit; new code for a phase lands with its tests.

---

## Git commit strategy

- **Granularity:** one commit per meaningful step — ideally one phase (or a slice of a phase) plus its tests. No "big bang" commits.
- **Order:** commit tests and code together when they pass; never commit a red suite intentionally.
- **Messages:** short, imperative summary line referencing the phase, e.g. `Add HTML tokenizer with position tracking`.
- **Workflow:**
  - Commit early while the suite is green.
  - Use small, focused diffs; separate refactors (Phase 8) from behavior changes.
  - Review with `git status` / `git diff` before committing; stage only intended files (never `node_modules/`, `.entire/`, logs).
- **Branching (optional):** work directly on the default branch for this learning project, or use a short-lived branch per phase if you want reviewable history.

---

## OpenCode usage

- **Planning:** keep this `plan.md` current as the source of truth; ask OpenCode to update it when scope changes.
- **Implementation:** ask OpenCode to implement **one phase at a time** — "implement Phase 2: tokenize the HTML, following plan.md" — rather than the whole program at once.
- **Tests:** ask OpenCode to write tests for a phase before or together with the implementation, then run `pytest` to verify.
- **Review:** use OpenCode to explain unfamiliar code, review diffs (`git diff`), and suggest refactors during Phase 8.
- **Guardrails:** explicitly tell OpenCode "do not implement other phases yet" to keep changes scoped; verify it only touched intended files.

---

## Entire usage

- **What it is:** the Entire plugin (`.entire/`, `.opencode/plugins/entire.ts`) provides session logging and git-ref checkpoints for this workspace.
- **Checkpoints:** Entire records git-ref checkpoints as you work, so you can recover or compare states if a change goes wrong — useful between phases.
- **Logs:** session activity is written under `.entire/logs/` for later review; these are tool artifacts, not project source.
- **Repository hygiene:** `.entire/` and `.opencode/` are tool-managed directories — keep them out of commits via `.gitignore` and don't hand-edit them.
- **Workflow fit:** let Entire checkpoint automatically after each phase commit; if an experiment fails, restore the last checkpoint and continue from a known-good state.
