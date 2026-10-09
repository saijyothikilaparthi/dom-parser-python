from dataclasses import dataclass


@dataclass(frozen=True)
class StartTag:
    name: str


@dataclass(frozen=True)
class EndTag:
    name: str


@dataclass(frozen=True)
class Text:
    content: str


Token = StartTag | EndTag | Text
