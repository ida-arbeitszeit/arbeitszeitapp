def is_possibly_an_email_address(text: str) -> bool:
    return (
        "@" in text
        and not text.startswith("@")
        and not text.endswith("@")
        and not text.startswith(" ")
        and not text.endswith(" ")
    )
