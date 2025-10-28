"""
PyTest fixtures for KanjiSVG testing.

Provides both properly loaded instances and improperly initialized instances
for testing happy paths and error conditions.

LLM DISCLOSURE:  This file Generated from Anthropic Claude Sonnet 4.5 in response to the below prompt

    give me a PyTest fixture containing a KanjiSVG instance, say KanjiSVG("書"), that executes the entire KanjiSVG load sequence as normal.  I want to use that fixture across all the test functions in the attached test_kanji_svg.py file that are doing this operation:

        glyph = "書"
        kanji_svg = KanjiSVG(glyph)

    Also, created faked out KanjiSVG fixtures that are  improperly initialized versions that we can use for error coverage in a companion test suite.

    Do not integrate the fixtures:  simply create them for review.

    Stash the "good" KanjiSVG in a list called good_kanji_svg.  
    Stash the faked out badly initialized KanjiSVG in a list called bad_kanji_svg.

The file has been reviewed and used with light modification.
"""
import pytest
from kanji_time.external_data.settings import KANJI_SVG_ZIP_PATH, KANJI_SVG_PATH
from kanji_time.external_data.kanji_svg import KanjiSVG, SVGDrawing
from kanji_time.svg_transform import Transform


# =============================================================================
# GOOD FIXTURES - Properly Loaded KanjiSVG Instances
# =============================================================================

@pytest.fixture
def loaded_kanji_svg_sho():
    """
    Properly loaded KanjiSVG instance for glyph 書 (sho - "write").
    
    This fixture executes the full load sequence, including:
    - ZIP file access
    - XML parsing
    - Stroke extraction
    - Label positioning
    - Radical identification
    
    Use this for happy-path testing where you need a fully functional
    KanjiSVG instance with real data.
    
    Returns:
        KanjiSVG: Fully loaded instance for 書
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)  # Fresh instance for each test
    kanji_svg.load()
    
    # Verify it loaded correctly
    assert kanji_svg.loaded, "KanjiSVG instance failed to load"
    assert len(kanji_svg.strokes) > 0, "No strokes loaded"
    assert len(kanji_svg._labels) == len(kanji_svg._strokes), "Strokes/labels mismatch"
    
    return kanji_svg


@pytest.fixture
def loaded_kanji_svg_to():
    """
    Properly loaded KanjiSVG instance for glyph 戸 (to - "door").
    
    Simpler kanji than 書, useful for tests that need fewer strokes.
    
    Returns:
        KanjiSVG: Fully loaded instance for 戸
    """
    glyph = "戸"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    kanji_svg.load()
    
    assert kanji_svg.loaded
    assert len(kanji_svg.strokes) > 0
    assert len(kanji_svg._labels) == len(kanji_svg._strokes)
    
    return kanji_svg


@pytest.fixture
def loaded_kanji_svg_tori():
    """
    Properly loaded KanjiSVG instance for glyph 鳥 (tori - "bird").
    
    Complex kanji with many strokes, useful for testing pagination
    and multi-row layouts.
    
    Returns:
        KanjiSVG: Fully loaded instance for 鳥
    """
    glyph = "鳥"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    kanji_svg.load()
    
    assert kanji_svg.loaded
    assert len(kanji_svg.strokes) > 0
    assert len(kanji_svg._labels) == len(kanji_svg._strokes)
    
    return kanji_svg


# Collect all good fixtures in a list for easy reference
GOOD_KANJI_SVG = [
    "loaded_kanji_svg_sho",
    "loaded_kanji_svg_to",
    "loaded_kanji_svg_tori",
]


# =============================================================================
# BAD FIXTURES - Improperly Initialized KanjiSVG Instances
# =============================================================================

@pytest.fixture
def unloaded_kanji_svg():
    """
    KanjiSVG instance that has NOT been loaded.
    
    Use this to test error handling when operations are attempted
    on unloaded instances.
    
    Returns:
        KanjiSVG: Unloaded instance (loaded=False, no strokes/labels)
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    # Deliberately don't call load()
    
    assert not kanji_svg.loaded
    return kanji_svg


@pytest.fixture
def kanji_svg_strokes_only():
    """
    KanjiSVG with strokes but NO labels.
    
    This is an invalid state - strokes and labels should always be paired.
    Use this to test defensive code that handles missing labels.
    
    Returns:
        KanjiSVG: Instance with strokes but no labels
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    
    # Manually set loaded flag and strokes without labels
    kanji_svg._loaded = True
    kanji_svg._strokes = ["M10,10 L90,10", "M10,20 L90,20"]
    kanji_svg._labels = []  # Empty labels - invalid state!
    
    # Set other required attributes to prevent AttributeError
    kanji_svg._viewbox = "0 0 100 100"
    kanji_svg._min_x = 0
    kanji_svg._min_y = 0
    kanji_svg._width = 100
    kanji_svg._height = 100
    
    return kanji_svg


@pytest.fixture
def kanji_svg_labels_only():
    """
    KanjiSVG with labels but NO strokes.
    
    Another invalid state - labels without corresponding strokes.
    Use this to test error handling for mismatched stroke/label counts.
    
    Returns:
        KanjiSVG: Instance with labels but no strokes
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    
    # Manually set loaded flag and labels without strokes
    kanji_svg._loaded = True
    kanji_svg._strokes = []
    
    # Create dummy labels with identity transforms
    transform = Transform()
    transform.translate(1, 1)  # Non-identity to be meaningful
    kanji_svg._labels = [(transform, "1"), (transform, "2")]
    
    # Set other required attributes
    kanji_svg._viewbox = "0 0 100 100"
    kanji_svg._min_x = 0
    kanji_svg._min_y = 0
    kanji_svg._width = 100
    kanji_svg._height = 100
    
    return kanji_svg


@pytest.fixture
def kanji_svg_empty_loaded():
    """
    KanjiSVG marked as loaded but with no actual data.
    
    Tests handling of edge case where load() was called but
    produced no strokes or labels.
    
    Returns:
        KanjiSVG: Instance marked loaded with empty data
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    
    # Set loaded but leave everything empty
    kanji_svg._loaded = True
    kanji_svg._strokes = []
    kanji_svg._labels = []
    
    # Set minimal required attributes
    kanji_svg._viewbox = "0 0 100 100"
    kanji_svg._min_x = 0
    kanji_svg._min_y = 0
    kanji_svg._width = 100
    kanji_svg._height = 100
    
    return kanji_svg


@pytest.fixture
def kanji_svg_mismatched_counts():
    """
    KanjiSVG with different numbers of strokes vs. labels.
    
    This violates the invariant that len(strokes) == len(labels).
    Use to test error detection for data inconsistency.
    
    Returns:
        KanjiSVG: Instance with 3 strokes but only 2 labels
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    
    kanji_svg._loaded = True
    kanji_svg._strokes = [
        "M10,10 L90,10",
        "M10,20 L90,20", 
        "M10,30 L90,30"
    ]
    
    # Only 2 labels for 3 strokes - MISMATCH!
    transform = Transform()
    transform.translate(1, 1)
    kanji_svg._labels = [(transform, "1"), (transform, "2")]
    
    # Set other required attributes
    kanji_svg._viewbox = "0 0 100 100"
    kanji_svg._min_x = 0
    kanji_svg._min_y = 0
    kanji_svg._width = 100
    kanji_svg._height = 100
    
    return kanji_svg


@pytest.fixture
def kanji_svg_bad_viewbox():
    """
    KanjiSVG with invalid viewbox dimensions.
    
    Tests handling of corrupted or malformed geometry data.
    
    Returns:
        KanjiSVG: Instance with zero-sized viewbox
    """
    glyph = "書"
    kanji_svg = KanjiSVG(glyph, no_cache=True)
    
    kanji_svg._loaded = True
    kanji_svg._strokes = ["M10,10 L90,10"]
    transform = Transform()
    transform.translate(1, 1)
    kanji_svg._labels = [(transform, "1")]
    
    # Invalid geometry - zero size!
    kanji_svg._viewbox = "0 0 0 0"
    kanji_svg._min_x = 0
    kanji_svg._min_y = 0
    kanji_svg._width = 0  # Invalid!
    kanji_svg._height = 0  # Invalid!
    
    return kanji_svg


# Collect all bad fixtures in a list for easy reference
BAD_KANJI_SVG = [
    "unloaded_kanji_svg",
    "kanji_svg_strokes_only",
    "kanji_svg_labels_only",
    "kanji_svg_empty_loaded",
    "kanji_svg_mismatched_counts",
    "kanji_svg_bad_viewbox",
]


# =============================================================================
# USAGE EXAMPLES (for documentation)
# =============================================================================

"""
USAGE EXAMPLES:

# Happy path test with properly loaded instance:
def test_draw_glyph(loaded_kanji_svg_sho):
    drawing = loaded_kanji_svg_sho.draw_glyph()
    assert isinstance(drawing, SVGDrawing)

# Error condition test with unloaded instance:
def test_draw_without_loading(unloaded_kanji_svg):
    with pytest.raises(AssertionError, match="loaded"):
        unloaded_kanji_svg.draw_glyph()

# Test defensive code for missing labels:
def test_draw_strokes_missing_labels(kanji_svg_strokes_only):
    # Should not crash, should handle gracefully
    drawing = kanji_svg_strokes_only.draw_glyph()
    assert isinstance(drawing, SVGDrawing)

# Parametrized test across all good fixtures:
@pytest.mark.parametrize("fixture_name", [
    "loaded_kanji_svg_sho",
    "loaded_kanji_svg_to", 
    "loaded_kanji_svg_tori"
])
def test_all_kanji_draw(fixture_name, request):
    kanji_svg = request.getfixturevalue(fixture_name)
    drawing = kanji_svg.draw_glyph()
    assert isinstance(drawing, SVGDrawing)
"""
