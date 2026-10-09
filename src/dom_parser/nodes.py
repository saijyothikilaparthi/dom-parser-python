from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Text:
    content: str


@dataclass
class Element:
    tag: str
    attributes: list[tuple[str, str]] = field(default_factory=list)
    children: list[Node] = field(default_factory=list)


@dataclass
class Document:
    children: list[Node] = field(default_factory=list)


Node = Element | Text
