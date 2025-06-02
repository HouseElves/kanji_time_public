"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import sys
import os

from sphinx.util import logging


logger = logging.getLogger(__name__)
sys.path.insert(0, os.path.abspath("../.."))


def setup(app):
    """Check for a NOTICE file before starting Spinx proper."""
    notice_path = os.path.join(app.srcdir, "../NOTICE")
    if not os.path.exists(notice_path):
        logger.warning("Missing NOTICE file at: %s — referenced by notice.rst", notice_path)


print(f"Python = {sys.executable}")
print(f"documenting modules in {os.path.abspath('../..')}")


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Kanji Time'
copyright = '2024, 2025 Andrew Milton'
author = 'Andrew Milton (code and docs)'
version = 'α - 0.1.0'
release = 'External Alpha 0.1.0.20250531'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.mermaid",
    "sphinx.ext.todo",
]

templates_path: list[str] = ['_templates']
exclude_patterns = [
    '**/parking_lot/',  # Exclude contents of parking_lot folders
    '**/parking_lot/*',  # Exclude the folders themselves (belt & suspenders)
]
todo_include_todos = True

mermaid_version = "11.6.0"
mermaid_include_elk = "0.1.4"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_theme_options = {
    'body_max_width' : 'none',
    'page_width': 'auto',
}
