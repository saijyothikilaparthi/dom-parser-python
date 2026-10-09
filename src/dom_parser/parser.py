from dom_parser.nodes import Document, Element, Text
from dom_parser.tokenizer import tokenize
from dom_parser.tokens import EndTag, StartTag, Token


class ParseError(Exception):
    pass


def build_tree(tokens: list[Token]) -> Document:
    document = Document()
    stack: list[Document | Element] = [document]
    for token in tokens:
        if isinstance(token, StartTag):
            element = Element(tag=token.name, attributes=list(token.attributes))
            stack[-1].children.append(element)
            stack.append(element)
        elif isinstance(token, EndTag):
            if len(stack) == 1:
                raise ParseError(f"Unexpected closing tag: </{token.name}>")
            if stack[-1].tag != token.name:
                raise ParseError(
                    f"Unexpected closing tag: </{token.name}> "
                    f"(expected </{stack[-1].tag}>)"
                )
            stack.pop()
        else:
            stack[-1].children.append(Text(content=token.content))
    if len(stack) > 1:
        raise ParseError(f"Unclosed tag: <{stack[-1].tag}>")
    return document


def parse(html: str) -> Document:
    return build_tree(tokenize(html))
