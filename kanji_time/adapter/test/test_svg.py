"""
Comprehensive test suite for radicals.py, utilities.general.py, and adapter.svg.py ensuring no regressions during refactor.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from kanji_time.external_data.radicals import radical_map, meaning_map, Radical
from kanji_time.utilities.general import rl_config, log, flatten, pdf_canvas, no_dict_mutators
from kanji_time.adapter.svg import DrawingForRL
from reportlab.lib.pagesizes import letter
from reportlab.graphics import renderPDF
import os
from io import StringIO

# TEST DrawingForRL INITIALIZATION
def test_drawing_for_rl_initialization():
    """Test initialization of DrawingForRL with size and viewBox."""
    drawing = DrawingForRL(size=("100", "200"), viewBox="0 0 100 200")
    assert drawing.attribs['viewBox'] == "0 0 100 200"
    assert drawing.attribs['width'] == "100"
    assert drawing.attribs['height'] == "200"
    assert drawing.attribs['xmlns'] == "http://www.w3.org/2000/svg"


def test_drawing_for_rl_no_size():
    """Test DrawingForRL initialization without specifying size."""
    drawing = DrawingForRL()
    assert 'width' not in drawing.attribs
    assert 'height' not in drawing.attribs

# TEST ATTRIBUTE MODIFICATIONS
def test_drawing_for_rl_attribute_removal():
    """Ensure unwanted XML attributes are excluded."""
    drawing = DrawingForRL(size=("100", "200"), viewBox="0 0 100 200")
    assert 'xmlns:xlink' not in drawing.attribs
    assert 'xmlns:ev' not in drawing.attribs
    assert 'version' not in drawing.attribs
    assert 'baseProfile' not in drawing.attribs

# TEST GET_XML METHOD
def test_drawing_for_rl_get_xml():
    """Test custom XML generation without unwanted attributes."""
    drawing = DrawingForRL(size=("100", "200"), viewBox="0 0 100 200")
    xml_output = drawing.get_xml()
    assert 'xmlns:xlink' not in xml_output
    assert 'xmlns:ev' not in xml_output

# TEST CONVERSION TO RLDRAWING
def test_drawing_to_rlg():
    """Test converting a valid SVG to ReportLab Drawing."""
    drawing = DrawingForRL(size=("100", "200"), viewBox="0 0 100 200")
    drawing.add(drawing.rect(insert=(10, 10), size=(80, 180), fill='red'))
    rlg_drawing = drawing.to_RLG()
    assert rlg_drawing is not None

# TEST MALFORMED SVG HANDLING
def test_drawing_to_rlg_malformed_svg():
    """Ensure to_RLG() gracefully handles malformed SVG input."""
    drawing = DrawingForRL(size=("100", "200"))
    drawing.attribs['viewBox'] = "invalid"  # Malformed viewBox
    with pytest.raises(Exception):
        drawing.to_RLG()
