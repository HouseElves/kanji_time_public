"""
Test suite for KanjiSVG class with full branch coverage.

TODO:  
    - Replace empty Transform instances [ie created with Transform()] with something meaningful
    - Forbid using improperly initialized KanjiSVG instances for happy path code tests
    - Add REQ tags to tie tests back to requirements (see test_distance.py pattern)
    - SPEC DEFECT: Define KanjiSVG invariants and preconditions:
        * draw_practice_strip() on empty instance → valid (empty grid)
        * draw_glyph() on ill-formed instance → currently undefined
        * Should draw_glyph() enforce len(strokes) == len(labels)?
        * Document decisions in requirements doc, then add REQ tags
"""
# pylint: disable=fixme

import io
import xml.etree.ElementTree as ET
import pytest
from unittest.mock import MagicMock, patch, mock_open

from kanji_time.adapter.svg import ReportLabDrawingFactory
from kanji_time.external_data.settings import KANJI_SVG_ZIP_PATH, KANJI_SVG_PATH
from kanji_time.external_data.kanji_svg import KanjiSVG, SVGDrawing
from kanji_time.external_data.test.test_kanji_dicts import hide_paths
from kanji_time.svg_transform import Transform
from kanji_time.visual.layout.region import Extent
from kanji_time.visual.layout.distance import Distance

# Test fixtures for well- and ill-formed KanjiSVG instances
from kanji_time.external_data.test.conftest import GOOD_KANJI_SVG, EXPECTED_STROKE_COUNTS


# TEST INITIALIZATION AND CACHING
@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_kanji_svg_initialization(kanji_svg_fixture, request):
    """Test initializing KanjiSVG instance."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    assert kanji_svg.loaded


def test_kanji_svg_caching():
    """Test that KanjiSVG instances are cached."""
    glyph = "戸"
    instance1 = KanjiSVG(glyph)
    instance2 = KanjiSVG(glyph)
    assert instance1 is instance2  # Cached instance reuse


# TEST LOADING LOGIC
def test_load_kanji_svg():
    """Test loading a Kanji SVG from XML."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    fake_svg_content = """
    <svg viewBox="0 0 100 150" xmlns="http://www.w3.org/2000/svg">
        <g id="kvg:StrokePaths_"""+glyph_code+"""">
            <g id="kvg:"""+glyph_code+"""">
                <path id="kvg:"""+glyph_code+"""-s1" type="x" d="M10,10 L90,10" />
            </g>
        </g>
    </svg>
    """
    with patch("zipfile.ZipFile.open", return_value=io.StringIO(fake_svg_content)):        
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_svg_content)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            kanji_svg.load()
            assert kanji_svg.loaded
            assert len(kanji_svg.strokes) == 1
            assert kanji_svg.viewbox == "0 0 100.0 150.0"


def test_no_zip_fallback():
    """Test that we try to open an uncompressed XML file if the ZIP does not exist."""
    glyph = "戸"
    hidden = [KANJI_SVG_ZIP_PATH]
    uncompressed = KANJI_SVG_PATH/f"{ord(glyph):05x}.svg"
    hider = hide_paths(hidden)

    def mock_target_does_not_exist(self):
        """Make the hider look like a class method for unittest.mock.patch."""
        return hider(self)

    assert all(mock_target_does_not_exist(target) is False for target in hidden)
    
    with patch("pathlib.Path.exists", mock_target_does_not_exist):
        assert all(target.exists() is False for target in hidden)  # Mocked: returns False
        if uncompressed.exists():
            glyph_root = KanjiSVG.kanji_vg_file(glyph)
            assert glyph_root is not None
        else:
            with pytest.raises(ValueError):
                glyph_root = KanjiSVG.kanji_vg_file(glyph)


def test_no_kanjivg_files():
    """Test that we try to open an uncompressed XML file if the GZIP does not exist, and fail if that doesn't exist either."""
    glyph = "戸"
    hidden = [KANJI_SVG_ZIP_PATH, KANJI_SVG_PATH/f"{ord(glyph):05x}.svg"] 
    hider = hide_paths(hidden)

    def mock_target_does_not_exist(self):
        """Make the hider look like a class method for unittest.mock.patch."""
        return hider(self)

    assert all(mock_target_does_not_exist(target) is False for target in hidden)
    
    with patch("pathlib.Path.exists", mock_target_does_not_exist):    
        assert all(target.exists() is False for target in hidden)  # Mocked: returns False
        with pytest.raises(ValueError):
            glyph_root = KanjiSVG.kanji_vg_file(glyph)


def test_double_load():
    """Test that a second load is a no-op."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    fake_svg_content = """
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g id="kvg:StrokePaths_"""+glyph_code+"""">
            <g id="kvg:"""+glyph_code+"""">
                <path id="kvg:"""+glyph_code+"""-s1" type="x" d="M10,10 L90,10" />
            </g>
        </g>
    </svg>
    """
    with patch("zipfile.ZipFile.open", return_value=io.StringIO(fake_svg_content)):        
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_svg_content)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            kanji_svg.load()
            assert kanji_svg.loaded
            assert len(kanji_svg.strokes) == 1
            kanji_svg.load()
            assert kanji_svg.loaded
            assert len(kanji_svg.strokes) == 1
            #: .. todo:: more invariance tests.


# TEST STROKE AND LABEL MANAGEMENT
def test_load_all_groups():
    """Test that stroke groups are loaded correctly."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    mock_group = ET.Element("g", id="kvg:"+glyph_code)
    subgroup = ET.SubElement(
        mock_group,
        ET.QName("http://www.w3.org/2000/svg", "g").text,
        id="kvg:"+glyph_code+"-g1"
    )
    _ = ET.SubElement(
        subgroup,
        ET.QName("http://www.w3.org/2000/svg", "path").text,
        d="M10,10 L90,10",
        type="x",
        id="kvg:"+glyph_code+"-s1"
    )
    strokes = kanji_svg._load_all_groups(mock_group)
    assert len(strokes) == 1
    assert strokes[0] == "M10,10 L90,10"


def test_load_group_radical():
    """Test that stroke groups are loaded correctly."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    # Top level group with a radical
    mock_group = ET.Element(
        "g",
        id="kvg:"+glyph_code,
        attrib={
            ET.QName("http://kanjivg.tagaini.net", "radical").text: "tradit"
        }
    )
    # Child group with multiple radicals
    subgroup = ET.SubElement(
        mock_group,
        ET.QName("http://www.w3.org/2000/svg", "g").text,
        id="kvg:"+glyph_code+"-g1",
        attrib={
            ET.QName("http://kanjivg.tagaini.net", "radical").text: "tradit, nielsen"
        }
    )
    # Empty child group with no radical
    _ = ET.SubElement(
        mock_group,
        ET.QName("http://www.w3.org/2000/svg", "g").text,
        id="kvg:"+glyph_code+"-g2"
    )
    # Stroke for the topmost group in the traditional radical
    _ = ET.SubElement(
        mock_group,
        ET.QName("http://www.w3.org/2000/svg", "path").text,
        d="M10,10 L90,10",
        type="x",
        id="kvg:"+glyph_code+"-s1"
    )
    # Stroke for the child group in the traditional & nielsen radical
    _ = ET.SubElement(
        subgroup,
        ET.QName("http://www.w3.org/2000/svg", "path").text,
        d="M10,10 L90,10",
        type="x",
        id="kvg:"+glyph_code+"-s2"
    )
    strokes = kanji_svg._load_all_groups(mock_group)
    assert len(strokes) == 2
    assert strokes[0] == "M10,10 L90,10"
    assert strokes[1] == "M10,10 L90,10"  # same same
    assert "" not in kanji_svg.radical_strokes
    assert "tradit" in kanji_svg.radical_strokes
    assert "nielsen" in kanji_svg.radical_strokes
    assert len(kanji_svg.radical_strokes) == 2
    assert kanji_svg.radical_strokes["tradit"] == [0, 1]
    assert kanji_svg.radical_strokes["nielsen"] == [1]
    #: .. todo:: I could walk the group hierarchy as well here.

    #: .. todo:: move this to be in the drawing tests.
    kanji_svg.loaded = True
    drawing = kanji_svg.draw_glyph(radical_only=True)
    assert isinstance(drawing, SVGDrawing)


def test_load_labels_from_kanji_svg():
    """Test that we can fully load a KanjiSVG and see the labels."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    fake_svg_content = """
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g id="kvg:StrokePaths_"""+glyph_code+"""">
            <g id="kvg:"""+glyph_code+"""">
                <path id="kvg:"""+glyph_code+"""-s1" type="x" d="M10,10 L90,10" />
            </g>
        </g>
        <g id="kvg:StrokeNumbers_"""+glyph_code+"""">
            <text transform="matrix(1 0 0 1 29.00 24.38)">1</text>
        </g>
    </svg>
    """
    with patch("zipfile.ZipFile.open", return_value=io.StringIO(fake_svg_content)):        
        with patch("xml.etree.ElementTree.parse") as mock_parse:
            mock_tree = MagicMock()
            mock_root = ET.fromstring(fake_svg_content)
            mock_tree.getroot.return_value = mock_root
            mock_parse.return_value = mock_tree
            kanji_svg.load()
            assert kanji_svg.loaded
            assert len(kanji_svg.strokes) == 1, f"len(kanji_svg.strokes) == {len(kanji_svg.strokes)} != 1 expected value"
            assert len(kanji_svg._labels) == len(kanji_svg.strokes), f"len(kanji_svg.strokes) == {len(kanji_svg.strokes)} != {len(kanji_svg._labels)} == len(kanji_svg._labels)"
            # Expected transform and text for label_elements[0]
            t = Transform()
            t.translate(29.00, 24.38)
            assert kanji_svg._labels[0][0].transform == t.transform
            assert kanji_svg._labels[0][1] == "1"

            #: .. todo:: more invariance tests.


def test_load_weirdo_tag():
    """Test that stroke groups are loaded correctly."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    mock_group = ET.Element("g", id="kvg:"+glyph_code)
    subgroup = ET.SubElement(
        mock_group,
        ET.QName("http://www.w3.org/2000/svg", "g").text,
        id="kvg:"+glyph_code+"-g1"
    )
    _ = ET.SubElement(
        subgroup,
        ET.QName("http://www.w3.org/2000/svg", "weirdo").text,
        id="kvg:"+glyph_code+"-w1"
    )
    strokes = kanji_svg._load_all_groups(mock_group)
    assert len(strokes) == 0


def test_load_labels():
    """Test that stroke labels are loaded."""
    glyph = "戸"
    glyph_code = f"{ord(glyph):05x}"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    labels_group = ET.Element("g", id="kvg:StrokeNumbers_"+glyph_code)
    label_elements = [
        ET.SubElement(
            labels_group,
            ET.QName("http://www.w3.org/2000/svg", "text").text,
            transform="matrix(1 0 0 1 29.00 24.38)",
        ),
        ET.SubElement(
            labels_group,
            ET.QName("http://www.w3.org/2000/svg", "text").text,
            transform="matrix(1 1 1 1 29.00 24.38)",
        )
    ]
    for i, elt in enumerate(label_elements):
        elt.text = str(i+1)

    kanji_svg._load_all_labels(labels_group, [])
    assert len(kanji_svg._labels) == len(label_elements)
    # Expected transform and text for label_elements[0]
    t = Transform()
    t.translate(29.00, 24.38)
    assert kanji_svg._labels[0][0].transform == t.transform
    assert kanji_svg._labels[0][1] == "1"
    # Expected transform and text for label_elements[1]
    t = Transform()
    t.matrix(1.0, 1.0, 1.0, 1.0, 29.00, 24.38)
    assert kanji_svg._labels[1][0].transform == t.transform
    assert kanji_svg._labels[1][1] == "2"


# TEST DRAWING METHODS
@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_draw_glyph(kanji_svg_fixture, request):
    """Test drawing the complete Kanji glyph."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    assert kanji_svg.loaded
    drawing = kanji_svg.draw_glyph()
    assert isinstance(drawing, SVGDrawing)
    #: .. todo:: validate all the draw glyph options
    drawing = kanji_svg.draw_glyph(no_center=True)
    assert isinstance(drawing, SVGDrawing)


@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_draw_stroke_steps(kanji_svg_fixture, request):
    """Test drawing Kanji stroke steps."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    assert kanji_svg.loaded
    drawing = kanji_svg.draw_stroke_steps(grid_columns=3)
    assert isinstance(drawing, SVGDrawing)


@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_draw_practice_strip(kanji_svg_fixture, request):
    """Test drawing practice strip."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    assert kanji_svg.loaded
    drawing = kanji_svg.draw_practice_strip(grid_columns=5)
    assert isinstance(drawing, SVGDrawing)


# TEST SVG UTILITIES
def test_draw_practice_axes():
    """Test drawing practice axes."""
    glyph = "戸"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    drawing = MagicMock()
    kanji_svg.draw_practice_axes(drawing, cell_count=(3, 3), cell_px_width=100, cell_px_height=100)
    assert drawing.add.call_count > 0


def test_draw_cell_dividers():
    """Test drawing cell dividers."""
    glyph = "戸"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    drawing = MagicMock()
    kanji_svg.draw_cell_dividers(drawing, cell_count=(3, 3), cell_px_width=100, cell_px_height=100)
    assert drawing.add.call_count > 0


# EDGE CASES
def test_load_invalid_svg():
    """Test handling of malformed SVG files."""
    glyph = "上"  # use a different glyph so we don't hit the cache
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    with patch("zipfile.ZipFile.open", return_value=io.StringIO("<svg></svg>")):        
        with pytest.raises(ValueError):
            kanji_svg.load()


def test_no_strokes_in_glyph(kanji_svg_labels_only):
    """Test handling of a glyph with no strokes."""
    kanji_svg = kanji_svg_labels_only
    assert kanji_svg.loaded
    assert len(kanji_svg._strokes) == 0
    drawing = kanji_svg.draw_glyph()
    assert isinstance(drawing, SVGDrawing)


# TEST STROKE COUNT VALIDATION
@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_kanji_svg_stroke_counts(kanji_svg_fixture, request):
    """Test stroke count matches expectation for known kanji."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    expected = EXPECTED_STROKE_COUNTS[kanji_svg_fixture]
    actual = len(kanji_svg.strokes)
    assert actual == expected, \
        f"{kanji_svg_fixture}: expected {expected} strokes, got {actual}"


# TEST PRACTICE STRIP DRAWING
@pytest.mark.parametrize("kanji_svg_fixture", GOOD_KANJI_SVG)
def test_kanji_svg_practice_strip(kanji_svg_fixture, request):
    """Test drawing practice strip."""
    kanji_svg = request.getfixturevalue(kanji_svg_fixture)
    assert kanji_svg.loaded
    strip_drawing = kanji_svg.draw_practice_strip(grid_columns=5)
    assert strip_drawing is not None
    assert isinstance(strip_drawing, SVGDrawing)


def test_kanji_svg_empty_practice_strip(kanji_svg_empty_loaded):
    """Test behavior when no strokes exist for practice strip."""
    kanji_svg = kanji_svg_empty_loaded
    assert kanji_svg.loaded
    assert len(kanji_svg._strokes) == 0
    strip_drawing = kanji_svg.draw_practice_strip(grid_columns=5)
    assert strip_drawing is not None


def test_reportlab_drawing_factory():
    """Verify that we can create a specialized drawing factory for ReportLab."""
    default_viewbox = "0 0 100 100"
    different_viewbox = "0 0 50 50"
    factory = ReportLabDrawingFactory(default_viewbox)
    d1 = factory()    
    assert d1.attribs['viewBox'] == default_viewbox
    d2 = factory(viewBox=different_viewbox)
    assert d2.attribs['viewBox'] == different_viewbox


# TEST ERROR CASES WITH BAD FIXTURES
def test_draw_glyph_unloaded(unloaded_kanji_svg):
    """Test that drawing fails on unloaded KanjiSVG."""
    # Generated by Anthropic Claude Sonnet 4.5
    with pytest.raises(AssertionError, match="Unexpected call"):
        unloaded_kanji_svg.draw_glyph()


def test_draw_strokes_missing_labels(kanji_svg_strokes_only):
    """Test behavior when strokes exist but labels are missing."""
    # Should not crash due to defensive with_labels check
    # Generated by Anthropic Claude Sonnet 4.5 & modified
    with pytest.raises(AssertionError, match="unexpected call"):
        kanji_svg_strokes_only.draw_stroke_steps(grid_columns=5)
    kanji_svg_strokes_only.loaded = True
    drawing = kanji_svg_strokes_only.draw_glyph()
    assert isinstance(drawing, SVGDrawing)
    

def test_draw_mismatched_counts(kanji_svg_mismatched_counts):
    """Test behavior when stroke/label counts don't match."""
    # Should either handle gracefully or raise IndexError
    # Generated by Anthropic Claude Sonnet 4.5 & modified
    with pytest.raises(AssertionError, match="unexpected call"):
        kanji_svg_mismatched_counts.draw_stroke_steps(grid_columns=5)
    kanji_svg_mismatched_counts.loaded = True
    with pytest.raises(IndexError):
        kanji_svg_mismatched_counts.draw_stroke_steps(grid_columns=5)
