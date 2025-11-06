"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import sys
import os

from sphinx.util import logging
from sphinx.application import Sphinx


logger = logging.getLogger(__name__)
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath('../../kanji_time/**/dev_notes'))

def setup(app: Sphinx):
    """
    Global Sphinx configuration.

        - Check for a NOTICE file before starting Spinx proper.
        - Connect a notifier for document builder post-initialization.

    A missing NOTICE file triggers a warning kick-out since we need it in notice.rst.
    TODO: shouldn't I have a more general dep checker as a build target?
    """
    notice_path = os.path.join(app.srcdir, "../NOTICE")
    if not os.path.exists(notice_path):
        logger.warning("Missing NOTICE file at: %s — referenced by notice.rst", notice_path)

    app.connect('builder-inited', on_builder_init_set_master_doc)

def on_builder_init_set_master_doc(app: Sphinx):
    """
    Set the master document based on builder type.

    Builder types are linear flow vs non-linear flow as defined in two lists local to this function.

        - Non-linear builders have tree navigation starting from  'index_nonlinear.rst'.
        - Linear builders have a single narrative flow with top-level TOC in 'index_linear.rst'.
    
    The build does not fail on an unrecognized builder type.
    This scenario causes a warning kick-out and the master_doc to default to a linear flow.
    """
    # Builders with tree navigation / non-linear browsing
    nonlinear_builders = [
        'html',      # Standard multi-page HTML
        'dirhtml',   # Directory-based HTML (foo/index.html structure)
    ]
    
    # Builders intended for linear/narrative reading
    linear_builders = [
        'singlehtml',  # Single-page HTML
        'latex',       # LaTeX → PDF
        'latexpdf',    # Direct PDF via LaTeX
        'text',        # Plain text
        'man',         # Unix manual pages
        'texinfo',     # Texinfo format
        'epub',        # EPUB ebooks (navigable but intended linear)
    ]

    # Master document names per flow type.
    # There should only be one of the master_docs included in the doc build.
    # The others need to go into the exclude patterns since Sphinx will try to build them unless we tell it otherwise.
    master_docs = {
        'linear_flow': 'index_linear',
        'nonlinear_flow': 'index_nonlinear'
    }
    all_masters = set(master_docs.values())
    
    # Determine the linearity  of the document flow by builder. Warn about unexpected builders and default to linear in that scenario.
    # NOTE: maybe I should have config option for kick-out prefix styles like "[KANJITIME] WARNING:"
    #
    builder = app.builder.name
    non_linear = builder in nonlinear_builders
    if not non_linear and builder not in linear_builders:
        print(f"[KANJITIME] WARNING: Unexpected builder '{builder}', defaulting to linear style.")

    # Now bind the master document for the flow type.
    flow_type = 'nonlinear_flow' if non_linear else 'linear_flow'    
    master_doc = master_docs[flow_type]
    excluded_masters = [
        # Include a file extension?  Don't include a file extension?
        # Sphinx is a little inconsistent on it's protocol. In this case, the exclusion list needs a full file name.
        f"{doc}.rst" for doc in all_masters if doc != master_doc  # more clear than "doc in (all_masters - {master_doc})"
    ]
    app.config.master_doc = master_doc
    app.config.exclude_patterns += excluded_masters

    NL = '\n\t'
    print("\n-----")
    print(f"[KANJITIME Sphinx] Builder: {builder} ({'non-linear' if non_linear else 'linear'}) → master_doc: {master_doc}")
    print(f"[KANJITIME Sphinx] Tags: {app.tags}")
    print(f"[KANJITIME Sphinx] Exclusions:{NL}{NL.join(app.config.exclude_patterns)}")
    print("-----\n")


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
