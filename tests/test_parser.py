from dom_parser.nodes import Document, Element, Text
from dom_parser.parser import build_tree, parse
from dom_parser.tokens import EndTag, StartTag, Text as TextToken


def test_empty_document():
    assert parse("") == Document(children=[])


def test_plain_text_only():
    assert parse("hello") == Document(children=[Text("hello")])


def test_single_element():
    assert parse("<p>Hello</p>") == Document(
        children=[Element(tag="p", children=[Text("Hello")])]
    )


def test_nested_elements():
    assert parse("<html><body><p>Hello</p></body></html>") == Document(
        children=[
            Element(
                tag="html",
                children=[
                    Element(
                        tag="body",
                        children=[Element(tag="p", children=[Text("Hello")])],
                    )
                ],
            )
        ]
    )


def test_sibling_elements():
    assert parse("<a></a><a></a>") == Document(
        children=[Element(tag="a"), Element(tag="a")]
    )


def test_text_before_between_and_after_tags():
    assert parse("before<p>mid</p>after") == Document(
        children=[
            Text("before"),
            Element(tag="p", children=[Text("mid")]),
            Text("after"),
        ]
    )


def test_multiple_top_level_elements():
    assert parse("<h1>t</h1><p>b</p>") == Document(
        children=[
            Element(tag="h1", children=[Text("t")]),
            Element(tag="p", children=[Text("b")]),
        ]
    )


def test_preserves_whitespace_only_text():
    html = "<p>a</p>\n\n  <p>b</p>\n"
    assert parse(html) == Document(
        children=[
            Element(tag="p", children=[Text("a")]),
            Text("\n\n  "),
            Element(tag="p", children=[Text("b")]),
            Text("\n"),
        ]
    )


def test_pretty_printed_document_keeps_whitespace_nodes():
    html = "<html>\n  <body>\n    <p>Hello</p>\n  </body>\n</html>\n"
    assert parse(html) == Document(
        children=[
            Element(
                tag="html",
                children=[
                    Text("\n  "),
                    Element(
                        tag="body",
                        children=[
                            Text("\n    "),
                            Element(tag="p", children=[Text("Hello")]),
                            Text("\n  "),
                        ],
                    ),
                    Text("\n"),
                ],
            ),
            Text("\n"),
        ]
    )


def test_crlf_preserved_in_text():
    assert parse("a\r\nb") == Document(children=[Text("a\r\nb")])


def test_attributes_default_to_empty():
    element = parse("<p>x</p>").children[0]
    assert element.attributes == []


def test_parses_attributes_onto_element_in_source_order():
    (element,) = parse('<div id="main" class="box">x</div>').children
    assert element.attributes == [("id", "main"), ("class", "box")]


def test_element_without_attributes_has_empty_attributes():
    (element,) = parse("<p>x</p>").children
    assert element.attributes == []


def test_attribute_with_empty_value_is_stored():
    (element,) = parse('<input value=""></input>').children
    assert element.attributes == [("value", "")]


def test_children_lists_are_independent():
    first = Element(tag="a")
    second = Element(tag="b")
    first.children.append(Text("x"))
    assert second.children == []


def test_build_tree_accepts_tokens():
    tokens = [StartTag("p"), TextToken("Hi"), EndTag("p")]
    assert build_tree(tokens) == Document(
        children=[Element(tag="p", children=[Text("Hi")])]
    )
