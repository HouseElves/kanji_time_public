"""
Test suite for kanji_dict.py and kanji_dic2.py modules with full branch coverage.
"""

import pathlib
import pytest
import io
from unittest.mock import patch, mock_open, MagicMock
import xml.etree.ElementTree as ET
from kanji_time.external_data.kanji_dict import load_kanjidict, get_glyph_xml as get_glyph_xml_dict, flatten_xml as flatten_kanjidict
from kanji_time.external_data.kanji_dic2 import load_kanjidic2, get_glyph_xml as get_glyph_xml_dic2, flatten_xml as flatten_kanjidic2
from kanji_time.external_data.settings import (
    KANJIDICT_GZIP_PATH, KANJIDIC2_GZIP_PATH,
    KANJIDICT_PATH, KANJIDIC2_PATH
)


class hide_paths:
    """
    Mock that a list of paths does not exist according to pathlib.Path.exists().

    Quick & dirty: no validation of any kind.

    :param hidden: a list of file system paths to hide fro Path.exists()
    """
    
    def __init__(self, hidden: list[pathlib.Path]):
        """Initialize a path hider."""
        self.hidden = hidden
        self.original_exists = pathlib.Path.exists

    def __call__(self, path: pathlib.Path) -> bool:
        """Return false if the path is in <self.hidden> else perform original behavior."""
        if path in self.hidden:
            return False
        return self.original_exists(path)


# TESTS FOR KANJI_DICT.PY

def test_load_kanjidict():
    """Test successful loading of KanjiDict XML."""
    fake_xml = "<mock_root><k_ele><keb>書</keb></k_ele></mock_root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            root = load_kanjidict()
            assert root.tag == "mock_root"


def test_no_gzip_fallback():
    """Test that we try to open an uncompressed XML file if the GZIP does not exist."""
    hidden = [KANJIDICT_GZIP_PATH, KANJIDIC2_GZIP_PATH] 
    hider = hide_paths(hidden)

    def mock_target_does_not_exist(self):
        """Make the hider look like a class method for unittest.mock.patch."""
        return hider(self)

    assert all(mock_target_does_not_exist(target) is False for target in hidden)
    
    with patch("pathlib.Path.exists", mock_target_does_not_exist):
        assert all(target.exists() is False for target in hidden)  # Mocked: returns False
        test_load_kanjidict()
        test_load_kanjidic2()


def test_no_dict_files():
    """Test that we try to open an uncompressed XML file if the GZIP does not exist, and fail if that doesn't exist either."""
    hidden = [KANJIDICT_GZIP_PATH, KANJIDIC2_GZIP_PATH, KANJIDICT_PATH, KANJIDIC2_PATH] 
    hider = hide_paths(hidden)

    def mock_target_does_not_exist(self):
        """Make the hider look like a class method for unittest.mock.patch."""
        return hider(self)

    assert all(mock_target_does_not_exist(target) is False for target in hidden)

    with patch("pathlib.Path.exists", mock_target_does_not_exist):    
        assert all(target.exists() is False for target in hidden)  # Mocked: returns False
        with pytest.raises(RuntimeError):
            test_load_kanjidict()
        with pytest.raises(RuntimeError):
            test_load_kanjidic2()


def test_get_glyph_xml_kanjidict():
    """Test retrieving glyph metadata from KanjiDict."""    
    glyph = "書"    
    # test a lookup into the loaded kanji_dict
    entries = list(get_glyph_xml_dict(glyph))
    assert len(entries) == 2  # 書 (write) has two distinct kanji dict entries
    # now test with some mocked XML
    fake_xml = f"<JMdict><k_ele><keb>{glyph}</keb></k_ele><k_ele><keb>xxx</keb></k_ele></JMdict>"
    with patch("gzip.open", return_value=io.StringIO(fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            entries = list(get_glyph_xml_dict(glyph, mock_root))
            assert len(entries) == 1  

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
    fake_xml = "<mock_root><character><literal>書</literal></character></mock_root>"
    with patch("builtins.open", mock_open(read_data=fake_xml)):
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_xml)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            root = load_kanjidic2()
            assert root.tag == "mock_root"


def test_get_glyph_xml_kanjidic2():
    """Test retrieving glyph metadata from KanjiDic2."""
    glyph = "書"
    entries = list(get_glyph_xml_dic2(glyph))
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
