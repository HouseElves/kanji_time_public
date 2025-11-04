.. region.py.dev_notes:

===========================
region.py Development Notes
===========================

For: :mod:`visual.frame.distaregionnce`

.. include:: /common

Future Feature Adds
-------------------

Generic Measures &  Geometry Enhancements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor all the arithmetic out to general purpose classes.
      There's experimental code mapping op groups into abstract algebra objects - monoid, group, field et al.
    - `__floordiv__` and `__truediv__` can operate on other measures of the same *unit* to produce a pure number.
    - Should there be a pure number (or pure ratio) unit in all the measure types?
    - Think about axis position and direction conventions - there's a clean way to do this with FP by passing around
      binary combinators appropriate to a coordinate system that map down to the conventionally oriented binops.
      The choice of conventional orientation doesn't matter as long as it's convenient and universal.

        - Look at :python:`StackLayoutStrategy.layout` -- there's some explicit coordinate assumptions.
          Probably the same story in :python:`Container.do_layout`

    - do I need an absolute and relative position in the geometry?
      Better named as `Offset` vs `Pos`.  :python:`Offset == (dx, dy)`.

        - This could impose a much pickier set of type constraints that ripples throughout the code.

            - `Pos` - `Pos` |rarr| `Offset`
            - `Pos` + `Pos` |rarr| meaningless.
            - `Pos` + `Offset` |rarr| `Pos`

          Whether this is a good or bad thing reamains to be seen. I *_do not want to overgeneralize_*.
        - Does this also mean two kinds of regions:  relative vs absolute |rarr| a `Subregion` maybe?
          :python:`Subregion == (Offset, Extent)`

    - a full featured notion of absolute and relative may need an awareness of global coordinates throughout
      *which violates one of the fundamental design commandments* that frames can be positioned arbitrarily just by moving their
      origin point.

        - There is merit to an absolute region in that the physical page itself has specific regions that *cannot* move: header, footer,
          t/b/l/r margins, printable area.
        - A root absolute region provides a single source of truth about the material origin of the entire coordinate system and about
          boundaries for relative regions that live inside of it.
        - I still worry that it will unnecessarily complicate code or tie my hands in the future trying to live up to an abstraction purity.

Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - w.r.t the thoughts on handling different coordinate systems in the geometry, a rendering technology will need to supply transforms
      to/from it's native coordinates (and ordinate data type!) and the conventional coordianate system adopted by the geometery.

        - Raises an interesting Q: should the geometry just have a global 'coordinate axis convention' setting that picks up from the
          rendering technology?
        - What if I want to change the convention setting?  Should I have multiple geometries with mapping functions between them?
          I.e. instantiate a geometry with immutable settings and well-known transforms to other geometries.
        - What if I totally change the rules and make one of my geometries projective or inversive... can I make them all cohabit nicely?


Code Review/Adjustments
-----------------------

    - Add: I can floordiv by another extent to produce a pure number - same story on truediv
    - Review: the `Region.__contains__` operator says it works in absolute coordinates - I have doubt.
      There's some real consistency/coherency issues to resolve about what 'containment' means for region-in-region or point-in-region w.r.t
      aboslute or relative coordinates
    - Review: `Region.__contains__` is one among many operators across `Region`, `Pos`, `Extent` that make strongly
      assumpition about the coordinate vector orientations (and probably handedness if we add a 3rd dimension).
      These operators will make the canonical use case for abstracting coordinate system transforms to a combinator layer.
    - Review: look at `Region.bounds` |rarr| this method is doing "unit propagation" as outlined in the proposed data forwarding feature.

