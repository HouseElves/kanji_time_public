Region Data Type
================

Python module: :mod:`visual.geometry.region`

A :class:`Region` represents a rectangular local coordinate system defined by an origin (:class:`Pos`) and a size (:class:`Extent`).

All :class:`ContentFrame` objects are positioned within a :class:`Region`.
This tactic allows each frame to operate in its own local coordinates independent of global page state.

:class:`Region` supports:

    - containment checks (`in`) against other regions, extents, and positions,
    - absolute bounding box queries via `.bounds(unit)`, and,
    - coordinate translation via `+ Pos` (e.g., for nesting or drawing offsets)

This class serves as the geometric contract passed to frames during layout and draw phases.

----

Code Link
---------

    :class:`kanji_time.visual.layout.region.Region`
