from collections.abc import Iterator

from dom_parser.nodes import Document, Element


def iter_elements(document: Document) -> Iterator[Element]:
    yield from _walk(document)


def _walk(node: Document | Element) -> Iterator[Element]:
    for child in node.children:
        if isinstance(child, Element):
            yield child
            yield from _walk(child)


def find_by_tag(document: Document, tag: str) -> list[Element]:
    return [element for element in iter_elements(document) if element.tag == tag]


def find_by_id(document: Document, element_id: str) -> list[Element]:
    return [
        element
        for element in iter_elements(document)
        if any(name == "id" and value == element_id for name, value in element.attributes)
    ]


def find_by_class(document: Document, class_name: str) -> list[Element]:
    return [
        element
        for element in iter_elements(document)
        if any(
            name == "class" and class_name in value.split()
            for name, value in element.attributes
        )
    ]
