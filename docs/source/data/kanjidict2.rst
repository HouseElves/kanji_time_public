Kanji Dict 2 Interface
======================

Python module: `external_data.kanji_dic2`

The `kanji_dic2` module provides a structured lookup into the KANJIDIC2 XML dataset. This dictionary includes readings, radicals, stroke
counts, grades, and semantic glosses for over 13,000 characters.

We expose a common interface:

    - `get_glyph_xml(glyph)` — fetches raw XML nodes for the specified kanji
    - `flatten_xml(entry)` — extracts important fields into a dictionary form

Unlike the original `kanji_dict`, this interface supports radical metadata, JLPT levels, Nelson indexes, and separate on/kun readings.

Kanji Time uses `kanji_dic2` as the primary source of kanji metadata in both practice sheets and summary reports.

----

.. automodule:: kanji_time.external_data.kanji_dic2
     :members:
