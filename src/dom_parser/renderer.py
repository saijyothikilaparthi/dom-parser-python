from dom_parser.nodes import Document, Element, Node, Text


def _is_whitespace_text(node: Node) -> bool:
    return isinstance(node, Text) and node.content.strip() == ""


def _label(node: Node) -> str:
    if isinstance(node, Element):
        if not node.attributes:
            return node.tag
        rendered = ", ".join(f'{name}="{value}"' for name, value in node.attributes)
        return f"{node.tag} [{rendered}]"
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


def _walk_text(nodes: list[Node]) -> list[str]:
    texts: list[str] = []
    for node in nodes:
        if isinstance(node, Text):
            if node.content.strip() != "":
                texts.append(node.content)
        elif isinstance(node, Element):
            texts.extend(_walk_text(node.children))
    return texts


def render_text(document: Document) -> str:
    texts = _walk_text(document.children)
    if not texts:
        return ""
    return "\n".join(texts) + "\n"
