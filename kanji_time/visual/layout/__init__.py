# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model 2D geometry for layout calculations.

Internal Dependencies
---------------------

.. mermaid::
    :caption: visual.layout - Internal Module Dependencies

    ---
    config:
        layout: elk
    ---
    flowchart TD

    region[region.py]
    anchor_point[anchor_point.py]
    distance[distance.py]
    stack_layout[stack_layout.py]

    region --> anchor_point
    region --> distance
    stack_layout --> region

"""
