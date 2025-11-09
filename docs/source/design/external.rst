.. _open_source_data:


Powered by Open Source Data
===========================

Kanji Time relies on trusted open-source datasets to provide accurate character definitions, readings, stroke counts, radicals,
and metadata for Japanese kanji and kana.

Currently integrated sources include:

    `KANJIDIC2 (kanji_dic2.xml) <https://www.edrdg.org/wiki/index.php/KANJIDIC_Project>`_
        A comprehensive database of kanji readings, meanings, frequencies, radicals, and metadata.

    `KANJIDICT (kanjidict.xml) <https://www.edrdg.org/wiki/index.php/KANJIDIC_Project>`_
         A companion dataset to KANJIDIC2 used primarily for additional glosses and semantic information.

    `KanjiSVG <https://kanjivg.tagaini.net/>`_
        A database of scalable vector graphics for (among other things) drawing kanji glyphs and illustrating kanji stroke order.

    `Unicode Radical Definitions <https://www.unicode.org/Public/15.1.0/ucd/CJKRadicals.txt>`_
        An extract from the Unicode database used to annotate traditional kanji radicals with Unicode-standard naming and references.

The first three of these sources contain XML data which Kanji Time loads and queries using custom XPath expressions that it passes to the `xml.etree.ElementTree` library.
The last source is a delimited text file obtained from the Unicode database that Kanji Time parses using regular expressions.

See :ref:`embedded_content` for credits and licensing for all 3rd party data used in Kanji Time.

----

Kanji Dictionary Interface
--------------------------

Kanji Time uses an informal interface common to the two dictionary sources to extract kanji-related data from XML.
The interface imposes consistent data access protocols between the two dictionaries.

    - `get_glyph_xml(glyph)` - to retrieve raw XML nodes
    - `flatten_xml(xml_node)` - to produce robust flat dictionaries keyed by field

The below dictionary wrapper modules implement both of these functions.

    - :doc:`../data/kanji_dict` - to obtain JMdict-EDICT glyph entries into gloss, reading, and part-of-speech fields, and,
    - :doc:`../data/kanjidict2` - for extended glyph information including radical values, stroke counts, JLPT levels, and multiple reading types.

The `KanjiReportData` and `PracticeSheetData` class definitions use these interfaces extensively to enrich rendered report content.

----

Kanji SVG Interface
-------------------

Kanji Time draws stroke order diagrams using scalable vector graphics files from the KanjiVG project.
These SVG files provide structural metadata for each stroke, radical group, and drawing order.

The `KanjiSVG` class acts as a cached drawing server.
Kanji Time instantiates this class for a particular glyph and uses the specialized drawing
methods (below) to create SVG content for output.

    - `draw_stroke_steps()` - creates a step-by-step sequence of cells with one new stroke per cell,
    - `draw_practice_strip()` - draws the kanji with each stroke labeled with its sequence number followed by empty practice cells, and,
    - `draw_glyph()` - draws the kanji with optional radical highlighting.

Internally, Kanji Time uses `svgwrite` for drawing SVG graphics and `xml.etree.ElementTree` for parsing them.
Each of the KanjiSVG drawing methods returns a ready-to-render SVG object that integrates directly into a report.

----

.. _radical_lookup_interface:

Radical Lookup Interface
------------------------

Kanji Time extracts radical metadata from a text file published by the Unicode Consortium (`CJKRadicals.txt`).
It maps each Kangxi radical number (1-214) to one or more Unicode characters, using the preferred form when available and falling back to
variants if needed.

The `Radical` class loads this data and provides accessors for

    - radical glyphs (`.glyphs`),
    - English glosses (`.interpretations`), and,
    - kana/romanized names (`.hiragana_names`, `.romanji_name`)

The containing module also exposes `radical_map()` and `meaning_map()` functions to retrieve the full lookup tables.

This mechanism supports radical labeling in reports and SVG rendering, and complements structural stroke information from KanjiVG.

