Radical Information
===================

Python module: `external_data.radicals`

This module maps Kangxi radical numbers (1-214) to Unicode character forms and glosses. Kanji Time uses this data to display radical
glyphs, glosses, and cross-referenced definitions in reports and SVG diagrams.

Kanji Time parses the `CJKRadicals.txt` file from the Unicode Character Database and extracts:

  - glyph variants for each radical (standard, simplified, and alternate),
  - gloss meanings and kana/romanji names, and,
  - supplemental metadata from KANJIDIC2 via `radical_name` and `rad_value` tags.

The main class, `Radical`, provides a rich object view of each radical’s shape and significance.

Two helper functions return global lookup tables:

  - `radical_map()` — radical number → (kangxi, cjk) Unicode pairs
  - `meaning_map()` — radical number → gloss definitions and tag-based meanings

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-external_data-radicals-py`

