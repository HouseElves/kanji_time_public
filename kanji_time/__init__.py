# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Define the global packaging parameters for Kanji Time.

Package Contents
----------------

.. toctree::
   :maxdepth: 1

   __main__.py          <__main__.py>
   settings.py          <settings.py>
   kanji_time_cli.py    <kanji_time_cli.py>
   svg_transform.py     <svg_transform.py>


"""

import pathlib

__version__ = "0.1.1-alpha-20250606"

#: root directory for the Python sources.
SOURCES_ROOT = pathlib.Path(__file__).parent
