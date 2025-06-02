Distance Data Type
===================

Python module: `visual.geometry.distance`

`Distance` is the foundational unit of length in Kanji Time. It models physical measurements like inches, centimeters, points, and pixels
using rational arithmetic for precision-safe layout operations.

The reasoning behind creating this Distance type is to have an immutable distance measurement that supports seemless conversion between
different units via properties.

For example:

.. code-block:: python

    width = Distance("3in")  # initialize as 3 inches
    point_width = width.pt   # express that 3 inches as points


Each `Distance` instance includes

    - a scalar `measure`
    - a unit of type `DistanceUnit`
    - an optional `at_least` constraint for stretchy or symbolic layouts

Supported Units
---------------

Distance supports fixed physical units (`in`, `mm`, `pt`) and symbolic units:

    - `*` means “fit to available space”
    - `!` means “infinite” (used for overflow or open-ended layouts)
    - `%`, `u`, and font-relative units are reserved for future or SVG contexts

Key Features
------------

  - Arithmetic and comparison operations between distances (e.g. `+`, `//`, `%`, `==`)
  - Unit conversions via `.to(target_unit)` or `.inch`, `.cm`, `.pt` accessors
  - Constraint-aware utilities like `.fix_to()` and `.parse()` for input

All layout primitives (`Extent`, `Region`, etc.) build on this class to maintain consistent and accurate measurement logic.

----

.. automodule:: kanji_time.visual.layout.distance
     :members:
