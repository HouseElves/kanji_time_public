# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model display areas containing particular types of renderable content.

Internal Dependencies
---------------------

.. mermaid::
    :caption: visual.frame - Internal Module Dependencies

    ---
    config:
        layout: elk
    ---
    flowchart TD

    container[container.py]
    page[page.py]
    simple_element[simple_element.py]
    drawing[drawing.py]
    empty_space[empty_space.py]
    formatted_text[formatted_text.py]
    page_rule[page_rule.py]

    page --> container
    drawing --> simple_element
    empty_space --> simple_element
    formatted_text --> simple_element
    page_rule --> simple_element

"""

