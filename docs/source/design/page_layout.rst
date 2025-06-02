.. include:: /common

.. _layout_model:

=====================
How Does Layout Work?
=====================

The guiding principal behind layout is *separation*.
Each block of reporting content lives inside its own rendering frame (or simply 'frame') that controls

    - the size of the content,
    - how that content is positioned inside a rectangle,
    - how that content is rendered, and,
    - how that content should be broken across page boundaries.

At the heart of this model is the :class:`RenderingFrame` protocol that defines a simple interface for these tasks and a set of state transitions
governing the frame's lifetime.

In more formal terms,

|    Kanji Time follows a compositional layout model inspired by page-based rendering engines and document frameworks.
|    Each page element implements a RenderingFrame that is responsible for measuring, laying out, and rendering itself or its children.

Kanji Time provides a set of built-in packaged frames from rendering common content, such as vector graphics and formatted text, to a PDF.

.. rubric:: Layout Model Contents
    :heading-level: 2

- :ref:`rendering_frame`
- :ref:`rendering_frame_lifecycle`
- :ref:`containers`
- :ref:`ws_management`
- :ref:`interactions`
- :ref:`page_management`

.. seealso::
    - See :ref:`builtin_frames` for more built-in packaged frames in Kanji Time.
    - See :ref:`layout ideas <layout_and_geometry>` for raw notes about the develop direction for layout.

----

.. _rendering_frame:

The RenderingFrame Protocol
---------------------------

The foundation of layout in Kanji Time is the `RenderingFrame` protocol.

All components that can be placed on a page — such as text boxes, glyphs, diagrams, or containers — conform to this protocol.

A `RenderingFrame` is responsible for three key phases in presenting its content:

1. **Measurement** - Evaluate the space requirements for a given render target.
2. **Layout** - Adjust child positions relative to a bounding region.
3. **Rendering** - Draw itself to the output surface [#surfaces]_ .

This protocol allows for arbitrary nesting and precise control over alignment, overflow handling, and visual structure.

Back to :ref:`layout_model`

.. rubric:: Footnotes
   :heading-level: 3

.. [#surfaces]

    For right now, the only available output surface is a PDF via ReportLab.

    .. seealso:: See :ref:`new rendering abstractions <rendering_technology>` for raw notes about future extensions to the available output surfaces.

----

.. _rendering_frame_lifecycle:

RenderingFrame State Lifecycle
------------------------------

A class implementing the :class:`RenderingFrame` behavior explicitly passes through several named states as each phase of measure/layout/render completes.

State transitions are triggered by invoking the core methods:

- ``measure(extent)``: Transition from the initial or reusable state to ``needs_layout``. This method calculates the size needed to contain the element content.

- ``do_layout(target_extent)``: Transition from ``needs_layout`` to ``ready``. This method reserves the actual layout space for the content within the provided extent.

- ``draw(c, region)``: Transition from ``ready`` to ``drawn`` and subsequently to either ``reusable`` (if content can be reused without measuring/layout) or ``all_data_consumed`` (if content is fully rendered and consumed).

In diagrammatic form:

.. mermaid::
    :caption: RenderingFrame state lifecycle.

    stateDiagram-v2
        [*] --> needs_layout: measure(extent)
        needs_layout --> ready: do_layout(target_extent)
        ready --> drawn: draw(c, region)
        drawn --> reusable: content reusable
        drawn --> all_data_consumed: content consumed
        reusable --> needs_layout: re-measure content


Back to :ref:`layout_model`

----

.. _containers:

Containers & Layout Strategies
------------------------------

Containers are :class:`RenderingFrame` implementations that can contain :class:`RenderingFrame` instances.
The key to a container is that it also contains a :class:`LayoutStrategy` instance.
The layout strategy for a container controls the positioning of the bounding rectangles for all the child frames of the container.

.. important:: *A layout strategy does not care about content - it only operates on the page and frame geometry with calls to :func:`RenderingFrame.measure()`.*

Layout Strategies
~~~~~~~~~~~~~~~~~

A layout strategy is an implementation of the :class:`LayoutStrategy` protocol.
There are only two methods to consider:

    :func:`LayoutStrategy.measure()`
        This method returns a minmial bounding box around a collection of content rectangles using this layout strategy.

    :func:`LayoutStrategy.layout()`
        This method positions a collection of content rectangles inside a bounding box using this strategy.

Built-in Strategies
~~~~~~~~~~~~~~~~~~~

Kanji Time provides two strategies in the box:  a horizontal stacker and a vertical stacker.

The minimalist strategy interface with these two stacking strategies combined with child containers cover a surprising amount of layout use cases!

For example, the Kanji Summary report can be described as

    #. a container with a vertical stack of 3 frames: a banner, a separator line, and definitions text, where,
    #. the banner frame is a container with a horizontal stack of 3 frames, where,
    #. the rightmost of these frames another vertical stack of 3 frames containing atomic content for the kanji radical.

Back to :ref:`layout_model`

----

.. _ws_management:

Whitespace Management
---------------------

A :class:`RenderingFrame` instance can indicate that can stretch to fit the available space by returning a "fit to" distance along one (or both) of its
dimensions from :func:`RenderingFrame.measure()`.  The layout strategies will allocate "left over" space from fixed size rendering frames to the "fit to"
distances. This simple tactic has proven to be surprisingly effective at covering a large number of use cases.

The middle "definitions" section of

Whitespace handling isn't perfect - but it meets expectations for the current usage.
There are many review issues and enhancements slated for the next development rounds.

.. seealso:: See :ref:`whitespace strategies <layout_and_geometry>` for planned enhancements to whitespace.

Back to :ref:`layout_model`

----

.. _interactions:

Class Interactions
------------------

The below diagram illustrates the relationships between the entities involved with layout.

.. mermaid::
    :name: layout_classes
    :caption: Kanji Time class interactions for layout.

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
        classDiagram
            direction TB

            class LayoutStrategy{
                <<abstract>>
                +measure(list[Extent] element_extents, fit_elements: Extent) -> Extent
                +layout(Extent target_extent, list[Extent] element_extents, Extent fit_elements) tuple[Extent, list[Region]]
            }
            class StackLayoutStrategy{
                <<realization>>
                +direction: enum(horizontal, vertical)
                +measure(list[Extent] element_extents, fit_elements: Extent) -> Extent
                +layout(elements: Sequence[RenderingFrame], target_extent: Extent) Region
            }
            class Container{
                + measure(extent: Extent) Extent
                + do_layout(target_extent: Extent) Region
            }
            LayoutStrategy <|-- StackLayoutStrategy
            Container ..> LayoutStrategy : uses during measure & do_layout

Back to :ref:`layout_model`

----

.. _page_management:

Page Management
---------------

A Page is a particular kind of container that has hard size boundaries.

Page management is handled externally by container elements such as ``KanjiReport`` and ``Page``. A new page is typically initiated through a
``begin_page(page_number)`` call, which resets layout and optionally introduces new content frames or layouts specific to the page number.
This provides flexibility in layout design for page-specific elements such as headers, banners, or footers.

Back to :ref:`layout_model`

