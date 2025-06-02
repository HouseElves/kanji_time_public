==============================
Atomic Content Rendering Frame
==============================

Python code file: visual/frame/simple_element.py

Simple elements are the leaves of the layout tree. These atomic frames do not contain children and are responsible for rendering a single unit of visual content.

Every `SimpleElement` conforms to the `RenderingFrame` protocol and implements default behaviors for:

- `measure()` - determines the space to reserve on the page
- `do_layout()` - positions the content within a local coordinate system
- `draw()` - executes visual rendering to a `DisplaySurface`

These defaults are intentionally simple and serve as a base class for more specialized elements like text blocks, glyphs, or inline diagrams.

.. caution::

   `SimpleElement` assumes that its requested size matches its layout size, which may not always hold true in real-world layouts.
   Subclasses are expected to override `measure()` and `do_layout()` if precision or adaptability is needed.

Inheritance Diagram:

.. mermaid::

    ---
    config:
        mermaid_include_elk: "0.1.7"
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB
        class RenderingFrame {
            <<interface>>
            + begin_page(int page_number) bool
            + measure(extent: Extent) Extent
            + do_layout(target_extent: Extent) Region
            + draw(c: DisplaySurface, region: Region) None
            + state() States
        }
        class SimpleElement {
            <abstract>
            -Size _requested_size
            -Size _layout_size
            -States _state
            +begin_page(int page_number) bool
            +measure(Extent extent) Extent
            +do_layout(Extent target_extent) Region
        }
        RenderingFrame <|-- SimpleElement

----

.. automodule:: kanji_time.visual.frame.simple_element
     :members:

