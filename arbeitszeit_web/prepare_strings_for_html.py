import html


def text_to_html(text: str) -> str:
    """
    Convert the characters &, < and > in strings to HTML-safe sequences.
    Converts CR and LF into line break.
    """
    safe_text = html.escape(text)
    return safe_text.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
