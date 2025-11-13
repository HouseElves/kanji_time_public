Kanji SVG Drawings
==================

Python module: `external_data.kanji_svg`

This module parses and renders stroke order diagrams for kanji characters using the open-source KanjiVG SVG dataset.
It supplies layout-aware drawing routines used in both the summary and practice sheet reports.

The `KanjiSVG` class acts as a cached drawing service that:

  - loads SVG stroke data for a glyph on demand,
  - parses stroke paths, labels, and radicals from XML, and,
  - offers methods to draw step-by-step stroke sequences, labeled characters, and ruled practice strips

Clients can call:

    - `draw_stroke_steps()` - create a diagram showing the stroke sequence for a glyph
    - `draw_practice_strip()` - draw the glyph and a row of empty cells for handwriting drills
    - `draw_glyph()` - draw the kanji alone or with radical strokes highlighted

Internally, Kanji Time uses `svgwrite` for drawing SVG graphics and `xml.etree.ElementTree` for parsing them.

The module includes caching, layout calculation, and drawing style helpers.


Module Header and API Reference
-------------------------------

:ref:`kanji_time-external_data-kanji_svg-py`
