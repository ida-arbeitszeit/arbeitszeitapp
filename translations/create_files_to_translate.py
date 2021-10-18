#!/usr/bin/env python
"""This script creates a file with  files that should be translated by gettext.
"""
import os
from pathlib import Path


def create_file():
    current_parent_path = Path(__file__).resolve().parent.parent
    # Add pathes here that have files that should be translated
    DIRECTORIES = ["arbeitszeit_web", "project"]
    pathes = [os.path.join(current_parent_path, directory) for directory in DIRECTORIES]
    with open("translations/files_to_translate.txt", "w") as f:
        for path in pathes:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".py"):
                        f.write(os.path.join(root, file) + "\n")


if __name__ == "__main__":
    create_file()
