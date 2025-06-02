"""
Global data for the external_data package.

.. only:: dev_notes

    - move all this into a YAML
    - can I do better for the project_root string and use a `stdpath.Path`?
      project_root is specifically for Sphinx so it's a little less whiney.
    - for that matter, is `project_root` even in the correct settings module?

----

.. seealso:: :doc:`dev_notes/settings_notes`

----

"""
import pathlib
import kanji_time.kanji_time as kt

# pylint: disable=invalid-name
project_root = pathlib.Path(kt.__file__).absolute().parent  # the directory of the CLI module.

radical_file = str(project_root / "external_data/CJKRadicals.txt") #: relative path to the Unicode Database CJKRadicals.txt file
kanjidic2_path = str(project_root / "external_data/kanjidic2.xml")  #: relative path to the Kanji Dict 2 XML file
kanjidict_path = str(project_root / "external_data/kanji_dict") #: relative path to the Kanji Dict XML file
kanji_svg = str(project_root / "external_data/kanji") #: relative path to Kanji SVG files directory
kanji_svg_path = str(project_root / "external_data/kanji/")    #: relative path to Kanji SVG files directory
