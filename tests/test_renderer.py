from dom_parser.parser import parse
from dom_parser.renderer import render


def test_render_empty_document():
    assert render(parse("")) == ".\n"


def test_render_whitespace_only_document():
    assert render(parse("   \n  ")) == ".\n"


def test_render_simple_text():
    assert render(parse("hello")) == '.\n└── "hello"\n'


def test_render_single_element():
    assert render(parse("<p>Hello</p>")) == '.\n└── p\n    └── "Hello"\n'


def test_render_nested_elements():
    html = "<html><body><p>Hello</p></body></html>"
    assert render(parse(html)) == (
        ".\n"
        "└── html\n"
        "    └── body\n"
        "        └── p\n"
        '            └── "Hello"\n'
    )


def test_render_sibling_elements():
    html = "<h1>t</h1><p>b</p>"
    assert render(parse(html)) == (
        ".\n"
        "├── h1\n"
        '│   └── "t"\n'
        "└── p\n"
        '    └── "b"\n'
    )


def test_render_deep_tree():
    html = "<a><b><c><d>x</d></c></b></a>"
    assert render(parse(html)) == (
        ".\n"
        "└── a\n"
        "    └── b\n"
        "        └── c\n"
        "            └── d\n"
        '                └── "x"\n'
    )


def test_render_ignores_whitespace_only_text():
    html = "<p>a</p>\n\n  <p>b</p>\n"
    assert render(parse(html)) == (
        ".\n"
        "├── p\n"
        '│   └── "a"\n'
        "└── p\n"
        '    └── "b"\n'
    )


def test_render_element_with_single_attribute():
    assert render(parse('<div id="main">x</div>')) == (
        '.\n└── div [id="main"]\n    └── "x"\n'
    )


def test_render_element_with_multiple_attributes():
    html = '<a href="/x" class="btn">go</a>'
    assert render(parse(html)) == (
        '.\n└── a [href="/x", class="btn"]\n    └── "go"\n'
    )


def test_render_element_with_empty_attribute_value():
    assert render(parse('<input value="">')) == '.\n└── input [value=""]\n'


def test_render_keeps_non_whitespace_text_at_top_level():
    html = "before<p>mid</p>after"
    assert render(parse(html)) == (
        ".\n"
        '├── "before"\n'
        "├── p\n"
        '│   └── "mid"\n'
        '└── "after"\n'
    )
