"""
Test suite for kanji_dict.py and kanji_dic2.py modules with full branch coverage.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
import xml.etree.ElementTree as ET
from kanji_time.external_data.kanji_dict import load_kanjidict, get_glyph_xml as get_glyph_xml_dict, flatten_xml as flatten_kanjidict
from kanji_time.external_data.kanji_dic2 import load_kanjidic2, get_glyph_xml as get_glyph_xml_dic2, flatten_xml as flatten_kanjidic2

# TESTS FOR KANJI_DICT.PY

def test_load_kanjidict():
    """Test successful loading of KanjiDict XML."""
    fake_xml = "<root><k_ele><keb>書</keb></k_ele></root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            root = load_kanjidict()
            assert root.tag == "root"

def test_get_glyph_xml_kanjidict():
    """Test retrieving glyph metadata from KanjiDict."""
    glyph = "書"
    fake_xml = f"<root><k_ele><keb>{glyph}</keb></k_ele></root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            #: .. todo:: this mock is not doing what it thinks that it's doing
            entries = list(get_glyph_xml_dict(glyph))
            assert len(entries) == 2  # 書 (write) has two distinct kanji dict entries

def test_flatten_kanjidict():
    """Test flattening XML entry from KanjiDict."""
    glyph = "書"
    entry_xml = ET.Element("entry")
    keb = ET.SubElement(entry_xml, "keb")
    keb.text = glyph
    flat = flatten_kanjidict(entry_xml)
    assert flat["glyph"] == [glyph]

# TESTS FOR KANJIDIC2.PY

def test_load_kanjidic2():
    """Test successful loading of KanjiDic2 XML."""
    fake_xml = "<root><character><literal>書</literal></character></root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            root = load_kanjidic2()
            assert root.tag == "root"

def test_get_glyph_xml_kanjidic2():
    """Test retrieving glyph metadata from KanjiDic2."""
    glyph = "書"
    fake_xml = f"<root><character><literal>{glyph}</literal></character></root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            entries = list(get_glyph_xml_dic2(glyph))
            assert len(entries) == 1

def test_flatten_kanjidic2():
    """Test flattening XML entry from KanjiDic2."""
    glyph = "書"
    entry_xml = ET.Element("character")
    literal = ET.SubElement(entry_xml, "literal")
    literal.text = glyph
    stroke_count = ET.SubElement(entry_xml, "stroke_count")
    stroke_count.text = "10"
    flat = flatten_kanjidic2(entry_xml)
    assert flat["kanji"] == glyph
    assert flat["stroke_count"] == "10"

# EDGE CASES

def test_empty_kanjidict_entry():
    """Test flattening with missing values in KanjiDict."""
    entry_xml = ET.Element("entry")
    flat = flatten_kanjidict(entry_xml)
    assert flat["glyph"] == []
    assert flat["frequency"] == []


def test_empty_kanjidic2_entry():
    """Test flattening with missing values in KanjiDic2."""
    entry_xml = ET.Element("character")
    flat = flatten_kanjidic2(entry_xml)
    assert flat["kanji"] is None
    assert flat["stroke_count"] is None
