from dom_parser.tokens import EndTag, StartTag, Text
from dom_parser.tokenizer import tokenize


def test_empty_input_produces_no_tokens():
    assert tokenize("") == []


def test_plain_text_is_one_token():
    assert tokenize("hello") == [Text("hello")]


def test_single_element():
    assert tokenize("<p>Hello</p>") == [StartTag("p"), Text("Hello"), EndTag("p")]


def test_nested_html():
    html = "<html><body><div><p>Hi</p></div></body></html>"
    assert tokenize(html) == [
        StartTag("html"),
        StartTag("body"),
        StartTag("div"),
        StartTag("p"),
        Text("Hi"),
        EndTag("p"),
        EndTag("div"),
        EndTag("body"),
        EndTag("html"),
    ]


def test_sibling_tags():
    assert tokenize("<a></a><a></a>") == [
        StartTag("a"),
        EndTag("a"),
        StartTag("a"),
        EndTag("a"),
    ]


def test_text_before_between_and_after_tags():
    html = "before<p>mid</p>after"
    assert tokenize(html) == [
        Text("before"),
        StartTag("p"),
        Text("mid"),
        EndTag("p"),
        Text("after"),
    ]


def test_preserves_whitespace_only_text_tokens():
    html = "<p>a</p>\n\n  <p>b</p>\n"
    assert tokenize(html) == [
        StartTag("p"),
        Text("a"),
        EndTag("p"),
        Text("\n\n  "),
        StartTag("p"),
        Text("b"),
        EndTag("p"),
        Text("\n"),
    ]


def test_leading_and_trailing_whitespace_text():
    assert tokenize("  <p>x</p>  ") == [
        Text("  "),
        StartTag("p"),
        Text("x"),
        EndTag("p"),
        Text("  "),
    ]


def test_source_order_preserved():
    html = "<a>1</a><b>2</b>"
    assert tokenize(html) == [
        StartTag("a"),
        Text("1"),
        EndTag("a"),
        StartTag("b"),
        Text("2"),
        EndTag("b"),
    ]


def test_parses_double_quoted_attributes():
    assert tokenize('<div id="main">x</div>') == [
        StartTag("div", (("id", "main"),)),
        Text("x"),
        EndTag("div"),
    ]


def test_parses_multiple_attributes_in_source_order():
    assert tokenize('<a href="/x" class="btn" id="go">t</a>') == [
        StartTag("a", (("href", "/x"), ("class", "btn"), ("id", "go"))),
        Text("t"),
        EndTag("a"),
    ]


def test_parses_empty_attribute_value():
    assert tokenize('<input value="">') == [StartTag("input", (("value", ""),))]


def test_attribute_without_value_is_ignored():
    assert tokenize("<input disabled>") == [StartTag("input")]


def test_unquoted_attribute_value_is_ignored():
    assert tokenize("<input value=abc>") == [StartTag("input")]


def test_crlf_inside_text_is_preserved():
    assert tokenize("a\r\nb") == [Text("a\r\nb")]
