=====================================
Auto-layout Rendering Frame Container
=====================================

Python code file: visual/frame/container.py

Containers are composite layout frames that own and manage multiple child `RenderingFrame` instances. They delegate sizing and positioning responsibilities to an injected `LayoutStrategy`.

Each child frame is placed into a layout region based on its measurement and the rules of the active strategy (e.g., stacked, fitted, or floating layouts).

Container frames are central to building vertically or horizontally composed report pages.

They are responsible for:

- Aggregating and synthesizing the layout and rendering state of their children
- Handling overflow and multi-page logic
- Coordinating two-pass measurement (first for fixed sizes, then for stretchy elements)
- Recursively triggering layout and draw operations for each child frame

Containers are fully compatible with the `RenderingFrame` protocol.

Class Relationships:

.. mermaid::

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB

        class RenderingFrame {
            <<interface>>
            + begin_page(int page_number) bool*
            + measure(extent: Extent) Extent*
            + do_layout(target_extent: Extent) Region*
            + draw(c: DisplaySurface, region: Region) None*
            + state() States
        }
        class LayoutStrategy {
            <<interface>>
            + measure(list[Extent], Extent) -> Extent
            + layout(Extent, list[Extent], Extent) -> (Extent, list[Region])
        }
        class Container {
            + begin_page(int page_number) bool
            + measure(extent: Extent) Extent
            + do_layout(target_extent: Extent) Region
            + draw(c: DisplaySurface, region: Region) None
            + state() States
        }
        Container --o LayoutStrategy : layout_strategy
        Container --o "n" RenderingFrame : child_elements

----

Container Code Link
-------------------

:ref:`kanji_time-visual-frame-container-py`
