# kanji_dic2.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Simple as possible interface into the local KanjiDic2 XML file.

The kanji_dic2.xml XML file is from the ELECTRONIC DICTIONARY RESEARCH AND DEVELOPMENT GROUP (EDRDG),
developed originally by Jim Breen & released to EDRDG in March 2000.

This data is licensed under the
`Creative Commons Attribution-ShareAlike 4.0 International License <https://creativecommons.org/licenses/by-sa/4.0/>`_.

No changes have been made to the original XML data.

- The original data are contained in this distribution 'as is' in the zip file 'external_data/kanjidic2.xml.gz' .
- This data file was originally obtained from
  `here <https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project#CURRENT_VERSION_&_DOWNLOAD>`_.

----

Kanji Time adds value to the Kanji Dict 2 data by defining a simple Python interface to extract XML nodes particular to a kanji (or kana) glyph.

----

"""

from collections.abc import Sequence, Generator
import gzip
import xml.etree.ElementTree as ET

from kanji_time.external_data.settings import KANJIDIC2_PATH, KANJIDIC2_GZIP_PATH, EXTERNAL_DATA_ROOT


# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


def load_kanjidic2() -> ET.Element:
    """
    Load the KanjiDict2 XML file and return the parsed tree.

    Attempt to load from a GZIP file first, then fall back to the filesystem.

    :return: the root of the parsed Kanji Dict XML tree.    
    """
    print("Loading extra kanji information...")
    tree : ET.ElementTree[ET.Element[str]] | None = None
    if KANJIDIC2_GZIP_PATH.exists():
        with gzip.open(KANJIDIC2_GZIP_PATH, 'rt', encoding='utf-8') as xml_file:
            logging.info(f"loading {KANJIDIC2_PATH.name} from {KANJIDIC2_GZIP_PATH}.")
            tree = ET.parse(xml_file)

    if tree is None and KANJIDIC2_PATH.exists():
        logging.info(f"loading {KANJIDIC2_PATH} from uncompressed data.")
        tree = ET.parse(KANJIDIC2_PATH)
    
    if tree is None:
        raise RuntimeError(f"Cannot load {KANJIDIC2_PATH}")
    
    assert tree is not None
    return tree.getroot()


def get_glyph_xml(kanji: str) -> Generator[ET.Element, None, None]:
    """
    Fetch metadata for a Kanji glyph from KanjiDict2.

    :param kanji:  Unicode codepoint for the kanji character to look up in KanjiDict

    :return: A lazy sequence of XML nodes containing metadata about the kanji.
    """
    root = kanjidic2_root
    glyph_xpath = lambda x: f".//character[literal='{x}']"
    return (e for e in root.findall(glyph_xpath(kanji)))


def flatten_xml(glyph_xml_record: ET.Element) -> dict[str, str | Sequence[str] | None]:
    """
    Extract data interesting to this version of Kanji Time from nodes in a KanjiDict2 XML tree to a flat dictionary.

    The resulting dictionary is a bit more robust w.r.t to missing data than the unprocessed XML nodes.

    :param glyph_xml_record: the root node for the data extraction process.
    :return: a dictionary of values.
    """
    return {
        "kanji": glyph_xml_record.find("literal").text if glyph_xml_record.find("literal") is not None else None,
        "kangxi radical": glyph_xml_record.find(".//rad_value[@rad_type='classical']").text
            if glyph_xml_record.find(".//rad_value[@rad_type='classical']") is not None else None,
        "Nelson radical": glyph_xml_record.find(".//rad_value[@rad_type='nelson_c']").text
            if glyph_xml_record.find(".//rad_value[@rad_type='nelson_c']") is not None else None,
        "stroke_count": glyph_xml_record.find(".//stroke_count").text
            if glyph_xml_record.find(".//stroke_count") is not None else None,
        "grade": glyph_xml_record.find(".//grade").text if glyph_xml_record.find(".//grade") is not None else None,
        "frequency": glyph_xml_record.find(".//freq").text if glyph_xml_record.find(".//freq") is not None else None,
        "variants": [v.text for v in glyph_xml_record.findall(".//variant") if v.text] or None,
        "radical name": [n.text for n in glyph_xml_record.findall(".//rad_name") if n.text] or None,
        "old jlpt level": glyph_xml_record.find(".//jlpt").text if glyph_xml_record.find(".//jlpt") is not None else None,
        "on_readings": [r.text for r in glyph_xml_record.findall(".//reading[@r_type='ja_on']") if r.text],
        "kun_readings": [r.text for r in glyph_xml_record.findall(".//reading[@r_type='ja_kun']") if r.text],
        "meanings": [m.text for m in glyph_xml_record.findall(".//meaning") if m.get("m_lang") is None and m.text],
        "nanori": [n.text for n in glyph_xml_record.findall(".//nanori") if n.text] or None,
    }


kanjidic2_root = load_kanjidic2()

if __name__ == '__main__':  # pragma: no cover
    for glyph in "書し台所":  # (chr(int("04e94", 16)), "戸", "書"):

        glyph_xml = get_glyph_xml(glyph)
        for entry in glyph_xml:
            flatdict = flatten_xml(entry)
            for k, v in flatdict.items():
                print(f"{k}: {v}")
            # if metadata["Nelson radical"]:
            #     print(f'Nelson Radical: {nelson_radicals[int(metadata["Nelson radical"])]}')
        print("==============")
