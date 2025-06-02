Region Data Type
================

Python module: `visual.geometry.region`

A `Region` represents a rectangular local coordinate system defined by an origin (`Pos`) and a size (`Extent`).

All `ContentFrame` objects are positioned within a `Region`.
This tactic allows each frame to operate in its own local coordinates independent of global page state.

`Region`` supports:

    - containment checks (`in`) against other regions, extents, and positions,
    - absolute bounding box queries via `.bounds(unit)`, and,
    - coordinate translation via `+ Pos` (e.g., for nesting or drawing offsets)

This class serves as the geometric contract passed to frames during layout and draw phases.

----

.. autoclass:: kanji_time.visual.layout.region.Region
     :members:
