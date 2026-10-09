from dom_parser.parser import parse
from dom_parser.query import find_by_class, find_by_id, find_by_tag
from dom_parser.renderer import render_text

FIXTURE_HTML = (
    "<html>"
    "<body>"
    '<div id="main" class="container a">'
    '<p class="a">One</p>'
    '<p class="b c">Two</p>'
    '<span id="main">Inner</span>'
    "</div>"
    "</body>"
    "</html>"
)


def test_find_by_tag_returns_matches_in_document_order():
    document = parse(FIXTURE_HTML)
    matches = find_by_tag(document, "p")
    assert [element.tag for element in matches] == ["p", "p"]
    assert [element.children[0].content for element in matches] == ["One", "Two"]


def test_find_by_tag_no_match():
    assert find_by_tag(parse(FIXTURE_HTML), "zzz") == []


def test_find_by_id_matches_exactly():
    document = parse(FIXTURE_HTML)
    matches = find_by_id(document, "main")
    assert [element.tag for element in matches] == ["div", "span"]


def test_find_by_id_does_not_match_partial():
    assert find_by_id(parse(FIXTURE_HTML), "mai") == []


def test_find_by_class_returns_all_matching_elements():
    document = parse(FIXTURE_HTML)
    matches = find_by_class(document, "a")
    assert [element.tag for element in matches] == ["div", "p"]


def test_find_by_class_matches_one_token_of_several():
    document = parse(FIXTURE_HTML)
    matches = find_by_class(document, "c")
    assert [element.tag for element in matches] == ["p"]
    assert matches[0].attributes == [("class", "b c")]


def test_find_by_class_includes_nested_matches_separately():
    document = parse('<div class="a"><div class="a">x</div></div>')
    matches = find_by_class(document, "a")
    assert len(matches) == 2


def test_render_text_in_document_order():
    html = "<div>\n  <p>One</p>\n  <p>Two</p>\n</div>\n"
    assert render_text(parse(html)) == "One\nTwo\n"


def test_render_text_walks_nested_elements():
    assert render_text(parse("<div>A<span>B</span>C</div>")) == "A\nB\nC\n"


def test_render_text_ignores_whitespace_only_text():
    assert render_text(parse("   \n  ")) == ""
