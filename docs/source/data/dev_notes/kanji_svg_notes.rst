.. _kanji_svg.py.dev_notes:

=================
Development Notes
=================

For: :mod:`external_data.kanji_svg`

.. include:: /common

Future Feature Adds
-------------------


XML Utilities
~~~~~~~~~~~~~

    - Pull in the XML-specific operations in the Kanji SVG loader
    - Connect dataclasses such as kanji_svg.KanjiSVG.StrokeGroup with the DTD parser such that I can autogenerate them from an XML source
    - Associate XML tag QNames with their property dataclass as an attribute.
      Consider an @XML_tag decorator on top of @dataclass to fill this in by magic.
    - Maybe tag dataclasses can include a `handler` classmethod that can go into a tag|rarr|handler dispatcher.
      If I'm going there, generic dispatching code would be convenient building on what's in `functools`.
    - Think about data cleansing for parameters on a tag dataclass:  who owns this code?

Thread Safety (for a multithreaded future)
------------------------------------------

    - Protect methods (like `kanji_svg.KanjiSVG.load`) with instance mutators with some kind of lock.
    - Maybe provide a guarantee mechanism that certain classs instances only live on one thread at a time?
      Possibly even a many reader / one writer model?

Linter Complaints
-----------------

    - :python:`external_data.kanji_svg` has several refactoring complaints from PyLint.
      I will be shuffling some code around here later. Bear these in mind.

        - class KanjiSVG - Too many instance attributes (17/7) (too-many-instance-attributes) |rarr| this will go away with an XML refactor
        - class StrokeGroup - Too many instance attributes (12/7) (too-many-instance-attributes) |rarr| ignore, it's a data class
        - method KanjiSVG._load_all_groups - Too many local variables (24/15) (too-many-locals) |rarr| this will go away with an XML refactor
        - method KanjiSVG.draw_strokes - Too many arguments (6/5) (too-many-arguments) (6/5) (too-many-positional-arguments) |rarr| worth investigating
        - method KanjiSVG.draw_practice_axes - Too many local variables (19/15) (too-many-locals) |rarr| worth investigating
        - method KanjiSVG.draw_stroke_steps Too many local variables (16/15) (too-many-locals) |rarr| worth investigating


Code Review/Adjustments
-----------------------

    - Review: does it make sense to mix caching with singletons?
    - Explore: is making a `cached_dict` type exploiting @lru_cache a reasonable abstraction?
    - Factor: pull out the Kanji SVG XML loader from the draw
    - Review: does DFLT_GLYPH_SIZE still belong to the KanjiSVG class? Make it a global constant?
    - Review: add strict type aliases for special purpose strings: SVG commands, Kanji parts, etc.?

        - consider a more active type that includes a "data cleanser" to normalize known input variants for XML parameters
        - Review: look at the svg_transform.Transform class in this context- maybe include specialized parsers?

    - Explore: is it worth creating Maybe-type wrappers? Python's None semantics are somewhat old-fashioned.
    - Review: `kanji_svg.KanjiSVG._load_all_groups` mutates `self` data attributes (such as _groups) directly instead of properly
      returning the data.
    - Factor: create a dispatch dictionary associating tags to tag handlers
    - Review: do the `completed_{attribs, groups}` audit sets in `kanji_svg.KanjiSVG._load_all_groups` need to be distinct?
    - Factor: eliminate the need for the `image_size` parameter in `kanji_svg.KanjiSVG.draw{glyph, stroke_steps}`.

        - Review: I could probably do this by instiating a drawing factory with a default image size.  Does that make sense in the
          abstractions?
        - Review: The whole drawing factory concept seems off.  I should be able to late-bind an image size whenever I want.
          The drawing instance itself is only a recipie for generating text, not the text itself.

    - Factor: replace the `loaded` flag on `kanji_svg.KanjiSVG` instances with a computed property
    - Review: consider a more efficient candy-stripe loop in `kanji_svg.KanjiSVG.draw_practice_axes` when drawing diagonal lines.
    - Review: express the image pixel size calculation as an inner product in `kanji_svg.KanjiSVG.draw_cell_dividers`?
      I would only go here if I have a more drawing flexible framework around this logic.
    - Review: should the `kanji_svg.KanjiSVG` class have more spacing options baked into the instance: inter-step margins, top/bottom margins?








