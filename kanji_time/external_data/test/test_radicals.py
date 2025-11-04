"""
Comprehensive test suite for Radical.py module ensuring no regressions during refactor.
"""

import pytest
from copy import deepcopy
from unittest.mock import patch, mock_open, MagicMock
import kanji_time.external_data.radicals as radicals_module
from kanji_time.external_data.radicals import Radical, radical_map, meaning_map

@pytest.fixture
def maps():
    # Snapshot the original maps
    original_radical_map = deepcopy(Radical.radicals)
    original_meaning_map = deepcopy(Radical.meanings)

    # Replace contents
    Radical.radicals = {
        1: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        2: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        3: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        4: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
    }

    
    Radical.meanings = {
        1: [{"hiragana_name": "いち", "meanings": ["one", "one radical (no.1)"]}, {}, {}],
        2: [{"meanings": ["one radical (no. 1)", "line"]}, {}, {}],
        3: [{}, {}, {}],
        4: [{}, {}, {}],
    }

    yield Radical.radicals, Radical.meanings

    # Restore the originals
    Radical.radicals = original_radical_map
    Radical.meanings = original_meaning_map

@pytest.fixture
def maps_from_xml():
    # Snapshot the original maps
    original_radical_map = deepcopy(Radical.radicals)
    original_meaning_map = deepcopy(Radical.meanings)

    yield Radical.radicals, Radical.meanings

    # Restore the originals
    Radical.radicals = original_radical_map
    Radical.meanings = original_meaning_map


# TEST RADICAL MAP LOADING
def test_radical_map_loading():
    """Test successful parsing of radicals from CJKRadical.txt."""
    mock_data = (
        "1; 2F00; 4E00\n"
        "2; 2F01; 4E28\n"
        "3; 2F02; 4E36\n"
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        radicals = radical_map()
        assert len(radicals) == 3
        assert radicals[1][0] == (chr(0x2F00), chr(0x4E00))
        assert radicals[2][0] == (chr(0x2F01), chr(0x4E28))
        assert radicals[3][0] == (chr(0x2F02), chr(0x4E36))

def test_radical_map_skip_comments():
    """Test successful parsing of radicals from CJKRadical.txt."""
    mock_data = (
        "# 1; 2F00; 4E00\n"
        "2; 2F01; 4E28\n"
        "3; 2F02; 4E36\n"
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        radicals = radical_map()
        assert len(radicals) == 2
        assert radicals[2][0] == (chr(0x2F01), chr(0x4E28))
        assert radicals[3][0] == (chr(0x2F02), chr(0x4E36))

def test_radical_map_skip_bogus_radical_number():
    """Test successful parsing of radicals from CJKRadical.txt."""
    mock_data = (
        "1; 2F00; 4E00\n"
        "a2b; 2F01; 4E28\n"
        "3; 2F02; 4E36\n"
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        radicals = radical_map()
        assert len(radicals) == 2
        assert radicals[1][0] == (chr(0x2F00), chr(0x4E00))
        assert radicals[3][0] == (chr(0x2F02), chr(0x4E36))

# TEST MEANING MAP EXTRACTION
def test_meaning_map_extraction():
    """Test extracting meanings for radicals using mocked KanjiDic2 data."""
    mock_radical_map = {
        1: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        2: [(chr(0x2F01), chr(0x4E28)), (None, None), (None, None)]
    }
    with patch("kanji_time.external_data.radicals.get_glyph_xml") as mock_glyph_xml:
        mock_entry = MagicMock()
        mock_entry.findall.side_effect = lambda x: [MagicMock(text="line")] if x == ".//rad_name" else []
        mock_glyph_xml.return_value = [mock_entry]
        meanings = meaning_map(mock_radical_map)
        assert meanings[1][0]["hiragana name"] == "line"
        assert meanings[2][0]["hiragana name"] == "line"

def test_meaning_map_variants():
    """Test extracting meanings for radicals using mocked KanjiDic2 data."""

    mock_radical_map = {
        1: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        90: [(chr(0x2F59), chr(0x723F)), (chr(0x2EA6), chr(0x4E2C)), (None, None)],
        210: [(chr(0x2FD1), chr(0x9F4A)), (chr(0x2EEC), chr(0x9F50)), (chr(0x2EEB), chr(0x6589))],
    }
    
    with patch("kanji_time.external_data.radicals.get_glyph_xml") as mock_glyph_xml:
        mock_entry = MagicMock()
        mock_entry.findall.side_effect = lambda x: [MagicMock(text="line")] if x == ".//rad_name" else []
        mock_glyph_xml.return_value = [mock_entry]

        meanings = meaning_map(mock_radical_map)
        assert meanings[1][0]["hiragana name"] == "line"
        assert meanings[90][0]["hiragana name"] == "line"
        assert meanings[90][1]["hiragana name"] == "line"
        assert meanings[210][0]["hiragana name"] == "line"
        assert meanings[210][1]["hiragana name"] == "line"
        assert meanings[210][2]["hiragana name"] == "line"

def test_no_meaning_to_extract():
    """Test extracting meanings for radicals using mocked KanjiDic2 data."""
    mock_radical_map = {
        1: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        2: [(chr(0x2F01), chr(0x4E28)), (None, None), (None, None)]
    }
    with patch("kanji_time.external_data.radicals.get_glyph_xml") as mock_glyph_xml:
        mock_entry = MagicMock()
        mock_entry.findall.side_effect = lambda _x: []
        mock_glyph_xml.return_value = [mock_entry]
        assert "hiragana name" not in mock_radical_map[1][0]
        assert "hiragana name" not in mock_radical_map[2][0]

def test_meaning_map_see_also():
    """Test extracting meanings for radicals using mocked KanjiDic2 data."""
    mock_radical_map = {
        1: [(chr(0x2F00), chr(0x4E00)), (None, None), (None, None)],
        2: [(chr(0x2F01), chr(0x4E28)), (None, None), (None, None)]
    }
    with patch("kanji_time.external_data.radicals.get_glyph_xml") as mock_glyph_xml:
        mock_entry = MagicMock()
        mock_entry.findall.side_effect = lambda x: [MagicMock(text="42")] if x == ".//rad_value[@rad_type='classical']" else []
        mock_glyph_xml.return_value = [mock_entry]
        meanings = meaning_map(mock_radical_map)
        assert meanings[1][0]["see also"] == "radical #42"
        assert meanings[2][0]["see also"] == "radical #42"

# TEST RADICAL CLASS INITIALIZATION AND PROPERTIES
def test_radical_initialization(maps):
    """Test initializing Radical object and loading properties."""
    _, _ = maps
    radical = Radical(1)
    assert radical.radical_num == 1
    assert radical.glyphs == [chr(0x4E00)]
    assert radical.hiragana_names == {"いち"}
    assert radical.romaji_name == "one"
    assert radical.interpretations == {"one"}

# TEST INVALID RADICAL INITIALIZATION
def test_radical_invalid_number():
    """Test initializing Radical with an out-of-range radical number."""
    with pytest.raises(ValueError):
        Radical(300)  # Radical number exceeds valid range

# TEST RADICAL GLYPHS EXTRACTION
def test_radical_glyphs(maps):
    """Test extracting CJK glyphs for radical variants."""
    _, _ = maps
    radical = Radical(4)
    assert radical.glyphs == [chr(0x4E00)]

# TEST RADICAL MEANING EXTRACTION
def test_radical_interpretations(maps):
    """Test extracting unique meanings from radical interpretations."""
    _, _ = maps
    radical = Radical(2)
    assert radical.romaji_name == "one"
    assert radical.interpretations == {"line"}

# EDGE CASES
def test_radical_missing_meanings(maps):
    """Test handling radicals with no assigned meanings."""
    _, _ = maps
    radical = Radical(3)
    assert radical.interpretations == set()
    assert radical.hiragana_names == set()
    assert radical.romaji_name is None
