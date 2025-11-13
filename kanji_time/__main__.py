# __main__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Top level entry point to Kanji Time via "Python -m"

.. seealso:: `__main__.py in the Python docs <https://docs.python.org/3.11/library/__main__.html#main-py-in-python-packages>`_

This entry point transfers control to the Kanji Time CLI in :mod:`kanji_time_cli`.
"""

def main():
    """
    Define the module entry point.

    Immediately transfers control to the Kanji Time CLI.
    """
    from kanji_time.kanji_time_cli import cli_entry_point
    cli_entry_point()


if __name__ == "__main__":
    main()