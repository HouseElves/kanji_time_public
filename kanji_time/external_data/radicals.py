# radicals.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Provide Unicode data for Kanji radicals cross-referenced into KanjiDic2.

.. admonition:: Licensing/Credits

    The source data contained in CJKRadicals.txt is copyright © 1991-2024 Unicode, Inc.
    The bundled file is an unaltered copy of the original data located online at
    https://www.unicode.org/Public/15.1.0/ucd/CJKRadicals.txt,

    Use of this source data is made under the Unicode License V3.

    The license allows for unrestricted use of the data provided that their copyright notice is included.

    In compliance with that requirement, the full text of the Unicode License V3 appears in the bundled file UnicodeV3.txt. It can also be viewed online at https://www.unicode.org/license.txt.

.. only:: dev_notes

    .. seealso:: :doc:`dev_notes/radicals_notes`

----

"""
# pylint: disable=fixme

from collections import defaultdict
from collections.abc import Mapping, Sequence
import re
import logging
logger = logging.getLogger(__name__)
# pylint: disable=wrong-import-position

from kanji_time.utilities.check_attrs import check_attrs, within, CheckOn
from kanji_time.external_data.kanji_dic2 import get_glyph_xml
from kanji_time.external_data import settings


cjk_supplement_range = range(0x2E80, 0x2EFF+1)  #: Unicode code points for CJK supplemental radicals
kangxi_range = range(0x2F00, 0x2FDF + 1)  #: Unicode code points for CJK kangxi radicals
cjk_range = range(0x4E00, 0x9FFF + 1)  #: Unicode code points for CJK Ideographs
cjk_compatibility_range = range(0x2F800, 0x2FA1F + 1)  #: Unicode code points for CJK alternate Ideographs
cjk_extension_h_range = range(0x31350, 0x323AF + 1)  #: Unicode code points for CJK Extras, range "H", for tertiary radical alternates


RadicalVariants = Sequence[tuple[str | None, str | None]]  #: Primary and alternate characters for a given radical
RadicalMap = Mapping[int, RadicalVariants]  #: Primary and alternate characters for all radicals by radical number
MeaningMap = Mapping[int, list[dict]]  #: Short meanings for all radicals by radical number

romaji_name = re.compile(r'(.*) radical \(no\. ?\d{1,3}\)')  #: Regular expression for extracting the romaji name for a radical character
radical_number_pattern = re.compile("([1-9][0-9]{0,2})(\'{0,2})")  #: Regular expression for extracting the radical number 1 to 214, inclusive


def radical_in_range(attrs: list[str], mode: CheckOn = CheckOn.Entry):
    """Provide a range bounds validation for radical numbers to test the generic attribute checker utility."""
    return check_attrs(*attrs, predicate=within(1, 214), mode=mode)


def radical_map() -> RadicalMap:
    """
    Construct a map from radical numbers to Unicode code points for radical variants.

    This loads up the CJKRadicals.txt file from the Unicode Database that gives possible code points
    (in order of preference) for each kanji radical, numbered 1 to 214.

    Reproduced from CJKRadicals.txt::

        There is one line per CJK radical number. Each line contains three
        fields, separated by a semicolon (';'). The first field is the
        CJK radical number. The second field is the CJK radical character,
        which may be empty if the CJK radical character is not included in
        the Kangxi Radicals block or the CJK Radicals Supplement block.
        The third field is the CJK unified ideograph.

        CJK radical numbers match the regular expression [1-9][0-9]{0,2}\'{0,2}
        and in particular they can end with one or two U+0027 ' APOSTROPHE characters.

    :return: map of radical numbers to code point variants
    """

    def new_list():
        """Construct an empty RadicalVariant sequence."""
        return [(None, None), (None, None), (None, None)]

    radical_forms_map = defaultdict(new_list)  #: Automatically constructs an empty RadicalVariant for new dictionary entries

    # Reproduced from CJKRadicals.txt:
    #
    #   There is one line per CJK radical number. Each line contains three
    #   fields, separated by a semicolon (';'). The first field is the
    #   CJK radical number. The second field is the CJK radical character,
    #   which may be empty if the CJK radical character is not included in
    #   the Kangxi Radicals block or the CJK Radicals Supplement block.
    #   The third field is the CJK unified ideograph.
    #
    #   CJK radical numbers match the regular expression [1-9][0-9]{0,2}\'{0,2}
    #   and in particular they can end with one or two U+0027 ' APOSTROPHE characters.
    #
    with open(settings.CJKRADICALS_PATH, encoding="utf-8") as ucd_radicals:
        while (line := ucd_radicals.readline().strip()):
            if line[0] == '#':  # ignore comments
                continue
            radical_number, radical_char, cjk_ideograph = map(str.strip, line.split(';'))
            id_match = radical_number_pattern.fullmatch(radical_number)
            if id_match is not None:
                radical_id = int(id_match[1])  # the radical_id number itself
                variant = len(id_match[2])  # the number of ticks after the radical_id number
                correspondence: tuple[str | None, ...] = tuple(
                    map(lambda x: chr(int(x, base=16)) if x.strip() else None, (radical_char, cjk_ideograph))
                )
                assert 1 <= radical_id <= 214, "Expected a kangxi radical number between 1 and 214"
                assert 0 <= variant <= 2, "Expected between 0 and 2 radical variants marked by ticks on the radical number."
                radical_forms_map[radical_id][variant] = correspondence  # type: ignore

    return radical_forms_map


def meaning_map(src_radical_map: RadicalMap) -> MeaningMap:
    """
    Construct a map from radical numbers to short meanings in English.

    :param src_radical_map: known code point representations for each radical number.

    :return: meaning map - meanings extracted from KanjiDict for each known radical code point.

    .. only:: dev_notes

        - more data / validation: xref names in src_radical_map with https://en.wikipedia.org/wiki/List_of_kanji_radicals_by_stroke_count

    """

    def new_list():
        return [{}, {}, {}]

    meanings = defaultdict(new_list)

    def map_meaning(pair, radical_id, i):
        """Do the query into KanjiDict for a particular radical variant."""
        # pylint: disable=redefined-outer-name
        kangxi, cjk = pair
        assert kangxi is None or ord(kangxi) in kangxi_range or ord(kangxi) in cjk_supplement_range
        assert ord(cjk) in cjk_range or ord(cjk) in cjk_extension_h_range

        character_xmls = get_glyph_xml(cjk)  # Issue:  this should be loading on-demand!
        for character_xml in character_xmls:
            radical_name = rad_name_xml[0].text if (rad_name_xml := character_xml.findall(".//rad_name")) else None
            if radical_name:
                meanings[radical_id][i]["hiragana name"] = radical_name
            radical = rad_value_xml[0].text if (rad_value_xml := character_xml.findall(".//rad_value[@rad_type='classical']")) else None
            if radical is not None and radical != radical_id:
                meanings[radical_id][i]["see also"] = f"radical #{radical}"
            meanings[radical_id][i]["meanings"] = [m.text for m in character_xml.findall(".//meaning") if m.attrib.get("m_lang") is None]

    # xref names in this with https://en.wikipedia.org/wiki/List_of_kanji_radicals_by_stroke_count
    for radical_id, [standard, variant_1, variant_2] in src_radical_map.items():
        # logging.info("%s: %s %s %s", radical_id, standard, variant_1, variant_2)
        map_meaning(standard, radical_id, 0)
        # logging.info("meaning 1 = '%s'", meanings[radical_id][0])
        assert variant_1[0] is None or ord(variant_1[0]) in cjk_supplement_range
        assert variant_1[1] is None or ord(variant_1[1]) in cjk_range
        if variant_1[1] is not None:
            map_meaning(variant_1, radical_id, 1)
            # logging.info("meaning 2 = '%s'", meanings[radical_id][1])
        assert variant_2[0] is None or ord(variant_2[0]) in cjk_supplement_range
        assert variant_2[1] is None or ord(variant_2[1]) in cjk_range or ord(variant_2[1]) in cjk_extension_h_range
        if variant_2[1] is not None:
            map_meaning(variant_2, radical_id, 2)
            # logging.info("meaning 3 = '%s'", meanings[radical_id][2])

    return meanings


class Radical:
    """
    Collect general information about a kanji radical from several sources into one container.

    :param radical_num: the radical number to investigate, from 1 to 214 (inclusive).

    .. mermaid::
        :name: cd_radicaldata
        :caption: Class relationships for the kanji radical data service.

        ---
        config:
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
                class Radical
                class RadicalVariants
                class MeaningVariants
                class MeaningMap
                class RadicalMap
                RadicalMap o-- "214" RadicalVariants
                MeaningMap o-- "214" MeaningVariants

                class Radical {
                    +radical_num : int 
                    +glyphs : set~str~ 
                    +interpretations : set~str~ 
                    +hiragana_names : set~str~ 
                    +romaji_name : set~str~ 
                }
                Radical *-- RadicalMap : radicals
                Radical *-- MeaningMap : meanings
                Radical o-- RadicalVariants : variants
                Radical o-- MeaningVariants : significance

    """

    radicals: RadicalMap | None = None  #: static mapping from radical number to unicode code points
    meanings: MeaningMap | None = None  #: static mapping from radical number to short English meanings

    def __new__(cls, *args, **kwargs):
        """
        Load up the radical and meaning maps on their first demand.

        .. only:: dev_notes

            - is Radical.__new__() thread safe?
        """
        if cls.radicals is None:
            cls.radicals = radical_map()
        if cls.meanings is None:
            cls.meanings = meaning_map(cls.radicals)
        return super().__new__(cls)

    def __init__(self, radical_num: int | str):
        """Initialize with the radical number."""
        # pylint: disable=unsubscriptable-object
        self.radical_num = radical_num = int(radical_num)
        if not 1 <= radical_num <= 214:
            raise ValueError("Radical number is out of range for the Kangxi radical set.")
        if self.radicals is None or self.meanings is None:
            raise ValueError("No radical database loaded.")
        assert self.radicals is not None
        self.variants = self.radicals[radical_num]
        assert self.meanings is not None
        self.significance = self.meanings[radical_num]

    @property
    def glyphs(self) -> list[str]:
        """Extract the CJK version of the radical variants."""
        return [
            cjk for (_, cjk) in self.variants
            if cjk is not None
        ]

    @property
    def hiragana_names(self) -> set[str]:
        """Extract the distinct Hiragana names for the radical."""
        return {
            m for meaning in self.significance  # type: ignore
            if (m := meaning.get("hiragana_name")) is not None
        }

    @property
    def romaji_name(self) -> str | None:
        """Extract the Romaji version of the radical name from the meanings."""
        for meaning in self.significance:  # type: ignore
            if (m := meaning.get("meanings")) is not None and (r := [match[1] for x in m if (match := romaji_name.match(x))]):
                return r[0]
        return None

    @property
    def interpretations(self) -> set[str]:
        """Extract the distinct meanings for the radical."""
        all_meaning_lists = [
            meaning.get("meanings")
            for meaning in self.significance
            if meaning and meaning.get("meanings") is not None
        ]
        return {
            e
            for meaning_list in all_meaning_lists
            for e in meaning_list  # type: ignore
            if not romaji_name.match(e)
        }


if __name__ == '__main__':  # pragma: no cover
    from contextlib import redirect_stdout

    loaded_radicals = radical_map()
    loaded_meanings = meaning_map(loaded_radicals)

    with open("totally_rad.txt", "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            for glyph_id, glyphs in loaded_radicals.items():
                mapping = zip(glyphs, loaded_meanings[glyph_id])
                print(f"Radical #{glyph_id}")

                ((kangxi, cjk), meaning_dict) = next(mapping, ((None, None), None))
                if all((kangxi is not None, cjk is not None, meaning_dict is not None)):
                    print(f'\tStandard: {kangxi}, U+{ord(kangxi)}, {cjk}, U+{ord(cjk)}')  # type: ignore
                    print("\t", "\n\t".join([f"{k}: {v}" for k, v in meaning_dict.items()]), sep="")  # type: ignore

                ((kangxi, cjk), meaning_dict) = next(mapping, ((None, None), None))
                if any((kangxi is None, cjk is None)):
                    print()
                    continue
                print(f'\tVariant #1: {kangxi}, U+{ord(kangxi)}, {cjk}, U+{ord(cjk)}')  # type: ignore
                if meaning_dict:
                    print("\t", "\n\t".join([f"{k}: {v}" for k, v in meaning_dict.items()]), sep="")

                ((kangxi, cjk), meaning_dict) = next(mapping, ((None, None), None))
                if any((kangxi is None, cjk is None)):
                    print()
                    continue
                print(f'\tVariant #2: {kangxi}, U+{ord(kangxi)}, {cjk}, U+{ord(cjk)}')  # type: ignore
                if meaning_dict:
                    print("\t", "\n\t".join([f"{k}: {v}" for k, v in meaning_dict.items()]), sep="")
                print()
