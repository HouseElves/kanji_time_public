"""
Simple as possible interface into the local KanjiDict XML file.

The kanji_dict XML file is from the ELECTRONIC DICTIONARY RESEARCH AND DEVELOPMENT GROUP (EDRDG),
developed originally by Jim Breen & released to EDRDG in March 2000.

This data is licensed under the
`Creative Commons Attribution-ShareAlike 4.0 International License <https://creativecommons.org/licenses/by-sa/4.0/>`_.

No changes have been made to the original XML data.

- The original data are contained in this distribution 'as is' in the zip file 'external_data/JMdict_e_examp.gz'.
- This data file was originally obtained from
  `here <https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project#CURRENT_VERSION_&_DOWNLOAD>`_.

----

Andrew Milton has created added value building on the Kanji Dict data by defining a simple Python interface to extract XML nodes
particular to a kanji (or kana) glyph as defined in this Python module.

----

"""

from collections.abc import Generator
import gzip
import xml.etree.ElementTree as ET

import kanji_time.external_data.settings as settings

# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


def load_kanjidict() -> ET.Element:
    """
    Load the KanjiDict XML file and return the parsed tree.

    Attempt to load from a GZIP file first, then fall back to the filesystem.

    :return: the root of the parsed Kanji Dict XML tree.    
    """
    print("Loading the kanji dictionary...")
    tree : ET.ElementTree[ET.Element[str]] | None = None
    if settings.KANJIDICT_GZIP_PATH.exists():
        with gzip.open(settings.KANJIDICT_GZIP_PATH, 'rt', encoding='utf-8') as xml_file:
            logging.info(f"loading {settings.KANJIDICT_PATH.name} from {settings.KANJIDICT_GZIP_PATH}.")
            tree = ET.parse(xml_file)

    if tree is None and settings.KANJIDICT_PATH.exists():
        logging.info(f"loading {settings.KANJIDICT_PATH} from uncompressed data.")
        tree = ET.parse(settings.KANJIDICT_PATH)
    
    if tree is None:
        raise RuntimeError(f"Cannot load {settings.KANJIDICT_PATH}")
    
    assert tree is not None
    return tree.getroot()


kanjidict_root = load_kanjidict()  #: root of the KanjiDict XML tree


def get_glyph_xml(kanji_glyph: str) -> Generator[ET.Element, None, None]:
    """
    Fetch metadata for a Kanji glyph from KanjiDict.

    :param kanji:  Unicode code-point for the kanji character to look up in KanjiDict
    :param root: the starting XML node for the search.

    :return: A lazy sequence of XML nodes containing metadata about the kanji.
    """
    xpath = lambda x: f".//k_ele[keb='{x}'].."  # f".//[keb='{x}']"
    return (e for e in kanjidict_root.findall(xpath(kanji_glyph)))


def flatten_xml(entry: ET.Element) -> dict[str, list[str] | list[dict[str, list[str]]]]:
    """
    Extract data interesting to this version of Kanji Time from nodes in a KanjiDict2 XML tree to a flat dictionary.

    The resulting dictionary is a bit more robust w.r.t to missing data than the unprocessed XML nodes.

    :param entry: The root node for the data extraction process.
    :return: a dictionary of values.
    """
    return {
        "glyph": [keb.text for keb in entry.findall(".//keb") if keb.text],
        "frequency": [pri.text for pri in entry.findall(".//ke_pri") if pri.text],
        "readings": [reb.text for reb in entry.findall(".//r_ele/reb") if reb.text],
        "senses": [
            {
                'pos': [pos.text for pos in sense.findall("./pos") if pos.text],
                'misc': [misc.text for misc in sense.findall("./misc") if misc.text],
                'gloss': [gloss.text for gloss in sense.findall("./gloss") if gloss.text],
            }
            for sense in entry.findall(".//sense")
        ]
    }

if __name__ == '__main__':  # pragma: no cover

    def print_kanjidict_info(kanji_glyph):
        """Dump out KanjiDict information for a glyph to make sure the XML loader is working."""
        glyph_xml = get_glyph_xml(kanji_glyph)
        for entry in glyph_xml:
            md = flatten_xml(entry)
            print(f"glyphs: {', '.join(md['glyph'])}")
            print(f"frequency: {', '.join(md['frequency'])}")
            print(f"readings: {', '.join(md['readings'])}")
            for i, s in enumerate(md['senses']):
                print(f"sense {i}")
                print(f"\tPOS: {', '.join(s['pos'])}")
                print(f"\tMisc: {', '.join(s['misc'])}")
                print(f"\t{'; '.join(s['gloss'])}")
            print()
        else:  # pylint: disable=useless-else-on-loop
            print("----")
        print()
        # display(Markdown(xml_to_markdown(ET.tostring(entry, encoding=\"unicode\"))))

    for kanji in "書し台所":
        print_kanjidict_info(kanji)
