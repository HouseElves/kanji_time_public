.. document.py.dev_notes:

=============================
document.py Development Notes
=============================

For: :mod:`reports.document.py`

.. include:: /common

Thread Safety (for a multithreaded future)
------------------------------------------

    - is thread safety an issue in the `kanji_summary.document.KanjiReportData` class?

Future Feature Adds
-------------------

Styles
~~~~~~

    - The styles that come in from ReportLab are very much JavaScript-inspired - they don't really play well in the Python idiom
    - Let's create something similar but derived off a ChainMap
    - Of course, we can also use a ChainMap for the style names
    - Consider a class/function decorator @styled:

        - provides a local `style` symbol implicity if it's not passed as an argument.  Put the default style name in the decorator.
        - intercepts kwargs off the function call to chain style overrides onto `style`
        - the page factory fetcher should also hand styling and overrides
        - pass the style plus any explicit overrides down to any called @styled function
        - useful in the Kanji Summary and Practice Sheet reports

    - Use case in the kanji vector drawings to change up the pen color for the radical
    - Give a YAML interface to configure all this.  Or a 3rd party CSS parser too, maybe?
    - See:

        - `reports.kanji_summary.KanjiReportData` methods
        - `reports.kanji_summary.document.build_data_object`
        - `external_data.kanji_svg.KanjiSVG`

      for some places where there are hardcoded dictionary styles.


Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - The text and drawing frames draw heavily on their ReportLab counterparts.
    - Data acquistion needs to be decoupled from its presentation - consider `kanji_summary.document.KanjiReportData` dataclass.
      It has ReportLab technology baked right into it - it should stop at the SVG and Simple HTML layers.
    - One concept for a technology driver is to serve up implementations of RenderingFrame via a factory, sort of how writesvg serves up SVG functionality.
    - Is it worth a generic protocol on behaviours?  I.e  ImplementsReportlab[Drawing] or some such?
    - This feature will also need to settle on some kind of universal coordinate system -- where is the origin and X/Y axis directions.
      It's possible that I can bury this in the `Region` handling, and simply interrogate the technology driver for its preferences.

Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - Need to make slop whitespace handling configurable through some kind of passed function like the layout strategies.
    - Could also add a property "accepts whitespace" to a RenderingFrame - parameterize it by AnchorPoint flags.
      The property indicates which side of a rendering frame against which it accepts arbitrary whitespace additions.

        - NB: this idea may not play well with horizontal vs vertical stacking strategies because of its absolute (vs relative) nature.
        - Consider a contextual or semantic variant similar to how "stack_dim" / "other_dim" work in `StackLayoutStrategy`

Size Contrants
~~~~~~~~~~~~~~

    - The "requested_size" property of the `RenderingFrame` is a little wishy-washy - I've established that it's a desired size to reserve
      but it's being used inconsistently
    - Formalize a constraint model on the `Distance` type: "exactly 2in" or "at most 50% of parent" or "at least 120pt", etc.


Code Review/Adjustments
-----------------------
    - Factor: decouple ReportLab technology from the `kanji_summary.document.KanjiReportData` class.
    - Review: how is `RenderingFrame.requested_size` being used in the various implementations - is it clean/consistent?
    - Rename: DrawingForRL to "SupportsReportLab[P]" where P is a protocol? Remember, generics are not real types in Python like in C++.
    - Add: some kind of fallback (to say text) if `kanji_summary.document.KanjiReportData.get_glyph_svg_drawing` can't get an SVG drawing.
      I would need a similar text glyph fallback for radicals, too.
    - Review: other fallback situations - say KanjiSVG for dict2 when looking at radicals?
    - Review: perhaps a partial appliction wrapper around `glyph_svg.draw_glyph` to make draw_radical in
      `kanji_summary.document.KanjiReportData.get_radical_svg_drawing`?
    - Review: a full-sized version of the radical drawing in `kanji_summary.document.KanjiReportData.get_radical_svg_drawing` instead of drawing
      the glyph w/ the non-radical strokes invisible?
    - Review: consider "no orphan" `FormattedText` rendering frames? Or should this be a style? Look at the use case in the kanji defintions
      body text in `kanji_summary.document.KanjiReportData.format_body_text`.
    - Factor: eliminte the `size` parameter to `kanji_summary.document.build_data_object`. The `Drawing` frame should supply it.
      See notes about `size` parameters in `external_data.kanji_svg.KanjiSVG.draw_stroke_steps` et al.
    - Factor: the style needs to be in options, not hardcoded, in `kanji_summary.document.build_data_object`
    - Big Issue: reconcile a big block of details from KanjiDict against multiple entries in KanjiDict2.
      `kanji_summary.document.build_data_object` only takes the _first_ from zip_longest(kanji_details, radical_details).
