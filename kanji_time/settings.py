# settings.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Global settings for Kanji Time.

Place all well-known symbols for the entire project across all packages in this module.

.. only:: dev_notes

    - move all this into a YAML
    - use file system Path objects where possible for directories.
    - I'm going to need help entries in the docs for all the settings once they are firmed up.

    .. seealso:: :doc:`dev_notes/settings_notes`

"""
# pylint: disable=invalid-name

#: Directory containing report add-ins
report_directory = "./reports/"
