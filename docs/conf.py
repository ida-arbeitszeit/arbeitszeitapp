import os
import sys

sys.path.insert(0, os.path.abspath(".."))


project = "arbeitszeitapp"
copyright = "2025, Gruppe Arbeitszeitapp"
author = "Gruppe Arbeitszeitapp"
html_theme = "sphinx_rtd_theme"
extensions = [
    "sphinx.ext.autodoc",
]
