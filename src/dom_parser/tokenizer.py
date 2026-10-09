from dom_parser.tokens import EndTag, StartTag, Text, Token


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
                parts = inner.split(None, 1)
                tokens.append(StartTag(parts[0] if parts else ""))
            i = end + 1
        else:
            next_open = html.find("<", i)
            if next_open == -1:
                next_open = length
            tokens.append(Text(html[i:next_open]))
            i = next_open
    return tokens
