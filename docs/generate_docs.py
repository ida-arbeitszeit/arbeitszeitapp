import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arbeitszeit_flask.config.options import CONFIG_OPTIONS  # noqa: E402

DOCS_PATH = "generated"


def make_rst_file(filename: str, content: str) -> None:
    os.makedirs(DOCS_PATH, exist_ok=True)
    filepath = os.path.join(DOCS_PATH, filename)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")


OPTIONS_SECTION = ""

for option in CONFIG_OPTIONS:
    description_lines = []
    for paragraph in option.description_paragraphs:
        description_lines.append(f"   {paragraph}")

    description_text = "\n".join(description_lines)

    example_text = f"\n\n   Example: ``{option.example}``" if option.example else ""
    default_text = f"\n\n   Default: ``{option.default}``" if option.default else ""

    OPTIONS_SECTION += f"""
.. py:data:: {option.name}

{description_text}{example_text}{default_text}
"""

if __name__ == "__main__":
    make_rst_file(
        "hosting.rst",
        f"""Hosting
=======

This application is designed to be self-hosted. The `IDA github organization <https://github.com/ida-arbeitszeit>`_
provides a repository that helps with hosting. If you are a community or organization that wants to host this application,
feel free to contact IDA (`gruppe_arbeitszeit@riseup.net <mailto:gruppe_arbeitszeit@riseup.net>`_) for help.

Configuration of the web server
-------------------------------

The application needs to be configured to function properly. This is
done via a configuration file. When starting ``arbeitszeitapp`` it
looks for configuration files in the following locations from top to
bottom. It loads the first configuration file it finds:

* Path set in ``ARBEITSZEITAPP_CONFIGURATION_PATH`` environment variable
* ``/etc/arbeitszeitapp/arbeitszeitapp.py``

The configuration file must be a valid python script.  Configuration
options are set as variables on the top level. The following
configuration options are available

{OPTIONS_SECTION}""",
    )
