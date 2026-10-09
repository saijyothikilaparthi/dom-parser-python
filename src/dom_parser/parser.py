from dom_parser.nodes import Document, Element, Text
from dom_parser.tokenizer import tokenize
from dom_parser.tokens import EndTag, StartTag, Token


class ParseError(Exception):
    pass


def build_tree(tokens: list[Token]) -> Document:
    document = Document()
    stack: list[Element] = []
    for token in tokens:
        if isinstance(token, StartTag):
            element = Element(tag=token.name, attributes=list(token.attributes))
            parent = stack[-1] if stack else document
            parent.children.append(element)
            stack.append(element)
        elif isinstance(token, EndTag):
            if not stack:
                raise ParseError(f"Unexpected closing tag: </{token.name}>")
            if stack[-1].tag != token.name:
                raise ParseError(
                    f"Unexpected closing tag: </{token.name}> "
                    f"(expected </{stack[-1].tag}>)"
                )
            stack.pop()
        else:
            parent = stack[-1] if stack else document
            parent.children.append(Text(content=token.content))
    if stack:
        raise ParseError(f"Unclosed tag: <{stack[-1].tag}>")
    return document


def parse(html: str) -> Document:
    return build_tree(tokenize(html))
