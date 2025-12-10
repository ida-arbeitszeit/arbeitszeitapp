import os
import sys

sys.path.insert(0, os.path.abspath(".."))


project = "workers-control"
copyright = "2026, ida-arbeitszeit"
author = "ida-arbeitszeit"
html_theme = "sphinx_rtd_theme"
extensions = [
    "sphinx.ext.autodoc",
]

html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]
