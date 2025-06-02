.. _open_source_data:

.. include:: open_data.rst

The first three of these sources contain XML data which we load and query using XPath expressions via the `xml.etree.ElementTree` standard library.
The last source is as delimited text file obtained from the Unicode database that we parse using regular expressions.

----

Kanji Dictionary Interface
--------------------------

Kanji Time uses a simple-as-possible informal interface to extract kanji-related dictionary data from XML.
There are two functions:

    - `get_glyph_xml(glyph)` - to retrieve raw XML nodes
    - `flatten_xml(xml_node)` - to produce robust flat dictionaries keyed by field

The exact fields contained in the dictionary produced by :func:`flatten_xml` vary by the XML source.

----

Kanji SVG Interface
-------------------

Kanji Time draws kanji glyphs and stroke order diagrams using scalable vector graphics files from the KanjiVG project.

The `KanjiSVG` class acts as a cached drawing server.
Instances of this class are bound to a particular Unicode kanji glyph.
Such an instance serves up SVG drawings as needed for the glyph:

    - `draw_stroke_steps()` - creates a step-by-step sequence of cells with one new stroke per cell,
    - `draw_practice_strip()` - draws the kanji with each stroke labeled with its sequence number followed by empty practice cells, and,
    - `draw_glyph()` - draws the kanji with optional radical highlighting.

Internally, we use `svgwrite` for drawing and `xml.etree.ElementTree` for SVG parsing.

----

Radical Lookup Interface
------------------------

Kanji Time extracts radical metadata from a text file published by the Unicode Consortium (`CJKRadicals.txt`).
Each Kangxi radical has a well-known number in the range 1-214.
The radical map associates each radical number with up to 3 distinct Unicode glyph variants for radical.

The `Radical` class is the interface into this bundle of glyphs that also provides value added data:

    - English glosses (`.interpretations`), and,
    - kana/romanized names (`.hiragana_names`, `.romanji_name`)

