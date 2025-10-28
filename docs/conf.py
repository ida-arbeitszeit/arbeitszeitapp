import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(".."))


def generate_rst_files():
    subprocess.run(["python", "generate_docs.py"], check=True)


generate_rst_files()

project = "arbeitszeitapp"
copyright = "2025, Gruppe Arbeitszeitapp"
author = "Gruppe Arbeitszeitapp"
html_theme = "sphinx_rtd_theme"
extensions = [
    "sphinx.ext.autodoc",
]
