Pos Data Type
=============

Python module: :mod:`visual.geometry.region`

The :class:`Pos` class - short for 'Position' - models a 2D point using :class:`Distance` values along the x and y axes.
It provides a simple but essential abstraction for positioning frames, regions, and layout elements.

:class:`Pos` supports:

  - vector arithmetic: `+` for translation, `-` via `__neg__()`,
  - containment tests (as part of `Extent` and `Region`), and,
  - utility methods such as `.zero` and `.logstr()` for diagnostics.

All `Region` origins are expressed as `Pos` instances.
Anchoring one `Extent` inside another with `anchor_at()` yields a `Pos` to indicate the proper positioning.

----

Code Links
----------

    :class:`kanji_time.visual.layout.region.Pos`
 