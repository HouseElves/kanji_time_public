"""
Global data for the external_data package.

.. only:: dev_notes

    - move all this into a YAML
    - can I do better for the PROJECT_ROOT string and use a `stdpath.Path`?
      PROJECT_ROOT is specifically for Sphinx so it's a little less whiney.
    - for that matter, is `PROJECT_ROOT` even in the correct settings module?

----

.. seealso:: :doc:`dev_notes/settings_notes`

----

"""
import pathlib
from kanji_time.external_data import EXTERNAL_DATA_ROOT

# pylint: disable=invalid-name

CJKRADICALS_FILE : pathlib.Path = "CJKRadicals.txt"  #: relative path to the Unicode Database CJKRadicals.txt file
KANJIDICT_FILE = "kanji_dict"
KANJIDICT_GZIP_FILE = "JMdict_e_examp.gz"
KANJIDIC2_FILE = "kanjidic2.xml"
KANJIDIC2_GZIP_FILE = "kanjidic2.xml.gz"
KANJI_SVG_DIR = "kanji"
KANJI_SVG_ZIP_FILE = "kanjivg-20240807-main.zip"

CJKRADICALS_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / CJKRADICALS_FILE

KANJIDICT_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJIDICT_FILE  #: relative path to the Kanji Dict XML file
KANJIDICT_GZIP_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJIDIC2_GZIP_FILE  #: relative path to the compressed Kanji Dict XML file

KANJIDIC2_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJIDIC2_FILE  #: relative path to the Kanji Dict 2 XML file
KANJIDIC2_GZIP_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJIDIC2_GZIP_FILE  #: relative path to the compressed Kanji Dict 2 XML file

KANJI_SVG_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJI_SVG_DIR  #: relative path to the Kanji SVG files directory
KANJI_SVG_ZIP_PATH : pathlib.Path = EXTERNAL_DATA_ROOT / KANJI_SVG_ZIP_FILE  #: relative path to the compressed Kanji SVG files directory
