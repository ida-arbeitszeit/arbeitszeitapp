import html

from flask import Markup


def text_to_html(text: str) -> Markup:
    """
    Convert the characters &, < and > in strings to HTML-safe sequences.
    Converts CR and LF into line break.
    Marks string as safe.
    """
    safe_text = html.escape(text, quote=False)
    return Markup(
        safe_text.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
    )
