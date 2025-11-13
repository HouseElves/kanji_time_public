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
sys.path.insert(0, os.path.abspath('./_ext'))

def set_html_theme(app: Sphinx):
    """
    Set options for HTML output

    See: https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
    """
    app.config.html_theme = 'furo' # 'alabaster'
    app.config.html_static_path = ['_static']
    app.config.html_css_files = ['custom.css']
    app.config.html_theme_options = {
        'body_max_width' : 'none',
        # 'page_width': 'auto',
        "navigation_with_keys": True,
        "sidebar_hide_name": False,
        }
    

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

    set_html_theme(app)


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
        'nonlinear_flow': 'index_nonlinear_cards'
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
    app.tags.add(flow_type)

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
copyright = '2024, 2025 Andrew Milton. This page is part of the Kanji Time documentation.'
author = 'Andrew Milton (code and docs)'
version = 'α - 0.1.0'
release = 'External Alpha 0.1.0.20250531'

# -- General configuration -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path: list[str] = ['_templates']
exclude_patterns = [
    '**/parking_lot/',  # Exclude contents of parking_lot folders
    '**/parking_lot/*',  # Exclude the folders themselves (belt & suspenders)
    # subsumed by furo:
    'docs/source/code_stubs/project_root.rst',
    'docs/source/code_stubs/adapter/index.rst',
    'docs/source/code_stubs/external_data/index.rst', 
    'docs/source/code_stubs/reports/index.rst',
    'docs/source/code_stubs/reports/kanji_summary/index.rst',
    'docs/source/code_stubs/reports/practice_sheet/index.rst',
    'docs/source/code_stubs/visual/index.rst',
    'docs/source/code_stubs/visual/frame/index.rst',
    'docs/source/code_stubs/visual/layout/index.rst',
    'docs/source/code_stubs/visual/protocol/index.rst',
    ]

extensions: list[str] = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.mermaid",
    "sphinx.ext.todo",
    "unique_section_ids",
    "sphinx_design",
    ]

# -- Extension Options ---------------------------------------------------------

# sphinx.ext.todo
todo_include_todos = True

# sphinxcontrib.mermaid
mermaid_version = "11"
mermaid_include_elk = "0"
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: false,
   theme: 'base',
    themeVariables: {
        // Core colors - work in both modes
        'primaryColor': '#8B9DC3',
        'primaryTextColor': '#1a1a1a',
        'primaryBorderColor': '#4A5568',
        
        'secondaryColor': '#C8D6E5',
        'secondaryTextColor': '#2d3748',
        'secondaryBorderColor': '#718096',
        
        'tertiaryColor': '#E2E8F0',
        'tertiaryTextColor': '#2d3748',
        'tertiaryBorderColor': '#A0AEC0',
        
        // Lines and edges
        'lineColor': '#4A5568',
        'edgeLabelBackground': 'rgba(255, 255, 255, 0.8)',
        
        // Text
        'textColor': '#2d3748',
        'fontSize': '14px',
        'fontFamily': 'inherit',
        
        // Backgrounds
        'background': 'transparent',
        'mainBkg': '#E8EEF5',
        'nodeBorder': '#4A5568',
        
        // Clusters/subgraphs
        'clusterBkg': 'rgba(200, 214, 229, 0.3)',
        'clusterBorder': '#718096',

        'actorBkg': '#C8D6E5',
        'actorBorder': '#4A5568',
        'actorTextColor': '#1a1a1a',
        'actorLineColor': '#4A5568',
        'signalColor': '#2d3748',
        'signalTextColor': '#1a1a1a',
        'labelBoxBkgColor': '#E2E8F0',
        'labelBoxBorderColor': '#718096',
        'labelTextColor': '#1a1a1a',
        'loopTextColor': '#1a1a1a',
        'activationBkgColor': '#A0AEC0',
        'activationBorderColor': '#4A5568',

        'stateLabelColor': '#1a1a1a',

        'noteBkgColor': '#FFF9C4',
        'noteTextColor': '#1a1a1a',
        'noteBorderColor': '#FBC02D',
        /* Optional: keep fonts consistent with theme */
        fontFamily: 'system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif'
  }
});
"""
# Control D3 version for zoom & Enable globally
d3_version = "7"  # default
mermaid_d3_zoom = True


# local unique_section_ids
unique_section_ids_separator = '-'  # Default separator
unique_section_ids_exclude = []     # List of docnames to skip
