Kanji Dict Interface
====================

Python module: `external_data.kanji_dict`

----

The `kanji_dict` module extracts entry-level dictionary data from the legacy KanjiDict XML dataset.
It contains readings, glosses, and grammatical tags for each character or kana.

The interface exposes:

    - `get_glyph_xml(glyph)` — fetches XML elements matching a given character
    - `flatten_xml(entry)` — converts those elements to a simplified dictionary form

The resulting dictionary includes orthographic variants, frequency indicators, kana readings, and semantic glosses grouped by sense.

This module supplements structured kanji metadata with looser dictionary-style glossing.

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-external_data-kanji_dict-py`
