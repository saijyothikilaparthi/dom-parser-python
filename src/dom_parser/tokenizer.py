from dom_parser.tokens import EndTag, StartTag, Text, Token


def _parse_attributes(text: str) -> tuple[tuple[str, str], ...]:
    attributes: list[tuple[str, str]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            i += 1
            continue
        start = i
        while i < n and text[i] != "=" and not text[i].isspace():
            i += 1
        name = text[start:i]
        while i < n and text[i].isspace():
            i += 1
        if i < n and text[i] == "=":
            i += 1
            while i < n and text[i].isspace():
                i += 1
            if i < n and text[i] == '"':
                i += 1
                value_start = i
                while i < n and text[i] != '"':
                    i += 1
                value = text[value_start:i]
                if i < n:
                    i += 1
                attributes.append((name, value))
            else:
                while i < n and not text[i].isspace():
                    i += 1
    return tuple(attributes)


def _parse_start_tag(inner: str) -> StartTag:
    i = 0
    n = len(inner)
    while i < n and not inner[i].isspace():
        i += 1
    return StartTag(name=inner[:i], attributes=_parse_attributes(inner[i:]))


def tokenize(html: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    length = len(html)
    while i < length:
        if html[i] == "<":
            end = html.find(">", i)
            if end == -1:
                tokens.append(Text(html[i:]))
                break
            inner = html[i + 1 : end]
            if inner.startswith("/"):
                tokens.append(EndTag(inner[1:].strip()))
            else:
                tokens.append(_parse_start_tag(inner))
            i = end + 1
        else:
            next_open = html.find("<", i)
            if next_open == -1:
                next_open = length
            tokens.append(Text(html[i:next_open]))
            i = next_open
    return tokens
