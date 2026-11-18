"""card(marker, name, gist, body_lines): the one place the report's collapsible card markup is written.

A card is one `<details>` block: a summary line (read marker, bold name, then the gist, the text after the name that
code computes from the dossier; an empty marker drops the marker and its space), a blank line, the body lines, a blank line, `</details>`. Escaping happens here, once:
the name and the gist get `&`, `<` and `>` escaped and are put on one line; a body line gets `<` escaped as `&lt;`
only, which is enough to stop any tag closing the card. Callers pass raw text and never escape it themselves."""
import re


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(marker, name, gist, body_lines):
    """The lines of one card, as a list (no trailing blank line). GIST may be empty or None: the summary then ends at the name."""
    one = lambda t: re.sub(r"\s+", " ", esc(t)).strip()
    summary = f"<details><summary>{marker + ' ' if marker else ''}<b>{one(name)}</b>" + (f" · {one(gist)}" if gist else "") + "</summary>"
    body = [str(l).replace("<", "&lt;") for l in body_lines]
    return [summary, ""] + body + ["", "</details>"]
