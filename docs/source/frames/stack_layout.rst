===========================================
Single Row or Column: Stack Layout Strategy
===========================================

Python code file: visual/layout/stack_layout.py

`StackLayoutStrategy` is a layout implementation that arranges elements in a linear stack, either horizontally (left to right) or vertically (top to bottom).

It conforms to the `LayoutStrategy` protocol and implements logic for computing both the minimum size of a stacked layout and the precise position of each frame inside it.

This strategy is ideal for most single-axis layouts such as:

- vertical blocks of text or figures
- horizontally aligned glyph rows
- multi-column headers

The direction (`horizontal` or `vertical`) is set at initialization. Stack position logic is abstracted through helpers for clarity and reuse.

Class Relationships
-------------------

.. mermaid::

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB

        class LayoutStrategy {
            <<interface>>
            + measure(list~Extent~, Extent) Extent
            + layout(Extent, list~Extent~, Extent) (Extent, list~Region~)
        }

        class StackLayoutStrategy {
            + measure(...)
            + layout(...)
        }

        LayoutStrategy <|-- StackLayoutStrategy

        class Container {
            + layout_strategy: LayoutStrategy
        }

        Container --> StackLayoutStrategy : injects layout behavior

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-visual-layout-stack_layout-py`
