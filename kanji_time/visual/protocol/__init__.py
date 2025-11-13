# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Define common interfaces to all visual elements.

Protocols
---------

.. mermaid::
    :caption: visual - Polymorphic Protocols

    ---
    config:
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        RenderingFrame ()-- visual.protocol
        LayoutStrategy ()-- visual.protocol

Package Contents
----------------

.. toctree::
   :maxdepth: 1
   :caption: Visual Protocols

   content.py <content.py>
   layout_strategy.py <layout_strategy.py>

"""
