from pathlib import Path

import pytest

from dom_parser.cli import main

TESTS_DIR = Path(__file__).resolve().parent
FIXTURES = TESTS_DIR / "fixtures"
GOLDEN = TESTS_DIR / "golden"

OUTPUT_CASES = [
    ("simple.html", [], "simple.default.out"),
    ("simple.html", ["--tree"], "simple.tree.out"),
    ("simple.html", ["--tokens"], "simple.tokens.out"),
    ("nested.html", ["--tree"], "nested.tree.out"),
    ("attributes.html", [], "attributes.default.out"),
    ("attributes.html", ["--tree"], "attributes.tree.out"),
    ("attributes.html", ["--find-tag", "p"], "attributes.find-tag-p.out"),
    ("attributes.html", ["--find-id", "main"], "attributes.find-id-main.out"),
    (
        "attributes.html",
        ["--find-class", "container"],
        "attributes.find-class-container.out",
    ),
    ("siblings.html", ["--tree"], "siblings.tree.out"),
    ("empty.html", [], "empty.default.out"),
    ("empty.html", ["--tree"], "empty.tree.out"),
    ("empty.html", ["--text"], "empty.text.out"),
    ("deep.html", ["--tree"], "deep.tree.out"),
    ("text_only.html", ["--tree"], "text_only.tree.out"),
    ("text_only.html", ["--text"], "text_only.text.out"),
    ("page.html", ["--tree"], "page.tree.out"),
    ("page.html", ["--text"], "page.text.out"),
    ("page.html", ["--find-tag", "li"], "page.find-tag-li.out"),
    ("page.html", ["--find-class", "item"], "page.find-class-item.out"),
    ("simple.html", ["--find-tag", "zzz"], "simple.find-tag-zzz.out"),
]

ERROR_CASES = [
    ("unclosed.html", ["--tree"], "unclosed.tree.err"),
    ("unexpected_close.html", ["--tree"], "unexpected_close.tree.err"),
    ("wrong_nesting.html", ["--tree"], "wrong_nesting.tree.err"),
]


@pytest.mark.parametrize("fixture,args,golden", OUTPUT_CASES)
def test_golden_output(fixture, args, golden, capsys):
    path = str(FIXTURES / fixture)
    assert main([path, *args]) == 0
    captured = capsys.readouterr()
    expected = (GOLDEN / golden).read_text(encoding="utf-8")
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize("fixture,args,golden", ERROR_CASES)
def test_golden_error(fixture, args, golden, capsys):
    path = str(FIXTURES / fixture)
    assert main([path, *args]) == 1
    captured = capsys.readouterr()
    expected = (GOLDEN / golden).read_text(encoding="utf-8")
    assert captured.err == expected
    assert captured.out == ""
