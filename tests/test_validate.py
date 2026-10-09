from pathlib import Path

import pytest

from dom_parser.parser import ParseError, parse

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_unclosed_tag_reports_exact_message():
    with pytest.raises(ParseError) as excinfo:
        parse(read_fixture("unclosed.html"))
    assert str(excinfo.value) == "Unclosed tag: <div>"


def test_unexpected_closing_tag_reports_exact_message():
    with pytest.raises(ParseError) as excinfo:
        parse(read_fixture("unexpected_close.html"))
    assert str(excinfo.value) == "Unexpected closing tag: </section>"


def test_wrong_nesting_reports_exact_message():
    with pytest.raises(ParseError) as excinfo:
        parse(read_fixture("wrong_nesting.html"))
    assert str(excinfo.value) == "Unexpected closing tag: </b> (expected </i>)"


def test_unclosed_inner_tag_is_reported():
    with pytest.raises(ParseError) as excinfo:
        parse("<div><span>text")
    assert str(excinfo.value) == "Unclosed tag: <span>"


def test_valid_html_does_not_raise():
    document = parse("<div><p>Hello</p></div>")
    assert document.children[0].tag == "div"


def test_validation_stops_at_first_error():
    with pytest.raises(ParseError) as excinfo:
        parse("</section><div></div>")
    assert str(excinfo.value) == "Unexpected closing tag: </section>"
