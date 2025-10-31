Extent Data Type
================

Python module: `visual.geometry.region`

`Extent` models the size of a 2D rectangular area, representing width and height as `Distance` objects.
It defines an area, but not a position, making it suitable for layout negotiation, bounding box calculation, and visual composition.

Extent includes arithmetic, anchoring, and scaling logic:

    - `+` and `-` combine or subtract widths/heights,
    - `anchor_at()` positions one extent inside another using a symbolic anchor (see below), and,
    - `coalesce()` fills in empty dimensions using a fallback value.

Extent also supports scalar math (e.g., `2 * Extent(...)`), union/intersection (`|` / `&`), and zero/fit-to constraints via `Extent.zero` and
`Extent.fit_to`.

This type plays a central role in layout sizing and is used extensively in frame measurement and layout negotiation.

AnchorPoint Enumeration
-----------------------

Python module: `visual.layout.anchor_point`

The `AnchorPoint` enum defines symbolic alignment flags for positioning one frame inside another.
The flags are compass-style anchor hints — such as `N`, `SW`, or `CENTER` — used by layout engines to place child content within a parent container.

This enum is used primarily by `Extent.anchor_at()` to align an inner extent relative to a larger one. It supports:

    - Cardinal directions: `N`, `S`, `E`, `W`
    - Corner alignments: `NE`, `NW`, `SE`, `SW`
    - Center alignment: `CENTER` (value = 0)

Flags may be combined using bitwise `|`:

.. code-block:: python

    anchor = AnchorPoint.N | AnchorPoint.W   # Align top-left
    origin = inner.anchor_at(anchor, outer)

These anchors are layout-agnostic but assume PDF-style coordinates by default (origin bottom-left).

----

.. autoclass:: kanji_time.visual.layout.region.Extent
     :members:

----

.. autoclass:: kanji_time.visual.layout.anchor_point.AnchorPoint
     :members:

