from importlib import resources
from typing import Callable, Dict

from markupsafe import Markup

ICON_PACKAGE = "arbeitszeit_flask.templates.icons"


def icon_file_reader(file_name: str) -> str:
    file_path = resources.files(ICON_PACKAGE).joinpath(file_name)
    with resources.as_file(file_path) as icon_file:
        return icon_file.read_text(encoding="utf-8")


def icon_filter(
    icon_name: str,
    reader: Callable[[str], str] = icon_file_reader,
    attrs: Dict[str, str] = {},
) -> Markup:
    """
    Transform an `icon_name` string into an HTML SVG icon representation
    and embed it into any Flask templates with customizable attributes.

    Purpose:
    --------
    The `icon_filter` function is designed to dynamically include HTML SVG
    icons in Flask templates. It reads Flask (Jinja2) HTML template files
    from a specified directory (`ICON_PATH`), injects additional HTML
    attributes into a `<svg>` tag, and returns the SVG content safely wrapped
    in a `Markup` object to prevent XSS attacks.

    Usage:
    ------
    The `icon_filter` function is registered as a template filter named `icon`
    in `arbeitszeit_flask/__init__.py`. Assuming an template icon file named
    `name.html` exists in the `ICON_PATH` directory, you can use the `icon`
    filter in a Flask template file as follows:

    ```html
    {{ "name"|icon }}
    ```

    This will include the `name` SVG icon in the HTML with the specified
    attributes.

    Extended Usage:
    ---------------
    If you want to extend or override SVG attributes, do the following:

    ```html
    {{ "name"|icon(attrs={"data-type": "toggle", "class": "foo bar baz"}) }}
    ```

    Error Handling:
    ---------------
    The function includes robust error handling to manage various issues that
    may arise:
    - If the SVG file is not found
    - If the SVG HTML template file is missing an <svg> tag
    - If any other exception occurs
    - If `FLASK_DEBUG` is set to `1` an exception will be raised
    - If `FLASK_DEBUG` is NOT set to `1` an HTML comment will be rendered

    Icon Implementation:
    --------------------
    To create new icons or modify existing ones, please refer to the concerning
    section in the developement guide.
    """
    try:
        return load_icon_with_name(icon_name, reader, attrs)
    except Exception as e:
        e.add_note(f'Error occurred while trying to load icon "{icon_name}".')
        raise e


def load_icon_with_name(
    icon_name: str, reader: Callable[[str], str], attrs: dict[str, str]
) -> Markup:
    # Treat empty icon_name as intentionally set null value
    if not icon_name.strip():
        return Markup("")
    file_name = f"{icon_name}.html"
    svg_content = reader(file_name)
    if "<svg" not in svg_content:
        raise ValueError(
            f'Icon "{icon_name}" does not contain valid SVG content: {svg_content}'
        )
    default_attributes = {
        "data-icon": icon_name,
        "width": "24px",
        "height": "20px",
        "aria-hidden": "true",
        "focusable": "false",
        "role": "img",
        "xmlns": "http://www.w3.org/2000/svg",
    }
    combined_attributes = {**default_attributes, **attrs}
    attributes_str = " ".join(
        [f'{key}="{value}"' for key, value in combined_attributes.items()]
    )
    svg_with_attrs = svg_content.replace("<svg", f"<svg {attributes_str}", 1)
    return Markup(svg_with_attrs)
