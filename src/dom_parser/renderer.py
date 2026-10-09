from dom_parser.nodes import Document, Element, Node, Text


def _is_whitespace_text(node: Node) -> bool:
    return isinstance(node, Text) and node.content.strip() == ""


def _label(node: Node) -> str:
    if isinstance(node, Element):
        return node.tag
    return f'"{node.content}"'


def _render_children(children: list[Node], prefix: str) -> list[str]:
    visible = [child for child in children if not _is_whitespace_text(child)]
    lines: list[str] = []
    for index, child in enumerate(visible):
        is_last = index == len(visible) - 1
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + _label(child))
        if isinstance(child, Element):
            extension = "    " if is_last else "│   "
            lines.extend(_render_children(child.children, prefix + extension))
    return lines


def render(document: Document) -> str:
    lines = ["."]
    lines.extend(_render_children(document.children, ""))
    return "\n".join(lines) + "\n"
