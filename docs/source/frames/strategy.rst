======================================================
Placing Frames in a Container: LayoutStrategy Protocol
======================================================

Python code file: visual/protocol/layout_strategy.py

The `LayoutStrategy` protocol defines the interface for layout policy objects.

A layout strategy is used by container frames to determine how to position their children within a bounded area.
Strategies decouple spatial logic from rendering, allowing multiple reusable algorithms to be implemented for arranging content.

.. note:: A LayoutStrategy never manipulates frame content. It only operates with the frame geometry.

Every strategy must implement two core methods:

- **`measure()`**: Accepts a list of element extents and returns the minimal size needed to accommodate them.
- **`layout()`**: Accepts a target region and element sizes, and returns their final positions as a list of `Region` objects.

This abstraction allows different strategies - like stacked, wrapped, or grid layouts - to be cleanly plugged into the layout pipeline.

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
            + measure(element_extents: list~Extent~, fit_elements: Extent) Extent
            + layout(target_extent: Extent, element_extents: list~Extent~, fit_elements: Extent) (Extent, list~Region~)
        }

        class Container {
            + layout_strategy: LayoutStrategy
        }

        Container --> LayoutStrategy : delegates positioning

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-visual-protocol-layout_strategy-py`]
