"""Test suite for FormattedText class with full branch coverage."""

import pytest
from unittest.mock import MagicMock
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.layout.region import Extent, Region, Pos
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.protocol.content import States


# ReportLab Text Paragraph Tests ----------------------------------------------------------------------------------------------------------- #


styles = getSampleStyleSheet()
normal_style = styles['Normal']


def in_typeface(font_name, text):
    """Helper function to apply a typeface (font) to a given text."""
    return f'<font name="{font_name}">{text}</font>'


def test_formatted_text_initialization():
    """
    Test initialization with paragraphs, anchor, and requested size.


    REQ: A formatted text frame type must be instantiated with an extent instance for its requested size, an anchor point in its parent,
         and a report lab paragraph instance that holds its content.
    REQ: A formatted text frame instance exposes its initialization parameters through like-named properties.
    REQ: After initialization, a formatted text frame instance is in the "new" state.
    """
    text = [Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    assert element.text == text
    assert element.anchor == AnchorPoint.CENTER
    assert element.requested_size == size
    assert element.state == States.new


def test_measure_with_text():
    """
    Test measure method properly calculates content size.

    REQ: The formatted text type implements a "measure" method from the rendering frame protocol that yields the actual extent required
         for its framed content including whitespace padding that is at least the requested size.
    REQ: The formatted test frame type exposes a "content size" property that is the minimum extent required to contain all the formatted
         text content.
    REQ: The formatted test frame type "content size" property is only meaningful after calling "measure".  TODO: not 100% true.
    REQ: The minimum width occupied by a formatted text frame instance is the width of its requested size.
    REQ: The minimum height occupied by a formatted text frame instance is the height of its requested size.
    REQ: The content height of a formatted text frame instance is the height required to fit all of its content at the requested size width.
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    measured_extent = element.measure(size)
    assert measured_extent.width >= size.width
    assert measured_extent.height >= size.height
    assert element.content_size.width >= size.width
    assert element.state == States.needs_layout


def test_measure_without_text():
    """
    Test measure returns zero extent when no text is provided.

    REQ: The formatted test frame type "content size" property is zero if there is no formatted text content in the frame.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, [])
    measured_extent = element.measure(size)
    assert measured_extent == size
    assert element.content_size == Extent.zero


def test_do_layout():
    """
    Test do_layout anchors the element correctly in target extent.

    REQ: The formatted text type implements a "do layout" method from the rendering frame protocol that yields a region of the same size
         as the target extent and an origin that positions the formatted text content in that region according to the frame's anchor point.
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    target_extent = Extent(Distance(20, "cm"), Distance(20, "cm"))
    element.measure(target_extent)
    region = element.do_layout(target_extent)
    assert region.origin.x >= Distance.zero
    assert region.origin.y >= Distance.zero
    assert element.state == States.ready


def test_do_layout_with_insufficient_space():
    """
    Test do_layout trims content size if target extent is too small.

    REQ: The formatted text type "do layout" method clips the content size downward if the target extent is too small.
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    small_extent = Extent(Distance(5, "cm"), Distance(2, "cm"))
    element.measure(size)
    region = element.do_layout(small_extent)
    assert region.extent.width <= small_extent.width
    assert region.extent.height <= small_extent.height


def test_draw():
    """
    Test drawing with a mock DisplaySurface.

    REQ: Drawing a formatted text frame instance faithfully renders as much formatted text content as will fit correctly positioned in
         the passed region.
    REQ: If a formatted text frame instance can fit all its content in the passed region then it indicates that it has no more to do by
         decorating the frame state with "all_data_consumed".
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    element.measure(size)
    element.do_layout(size)
    element.draw(mock_canvas, region)
    assert element.state & (States.drawn | States.all_data_consumed)


def test_draw_do_not_consume():
    """
    Test drawing with a mock DisplaySurface.

    REQ:  If a formatted text frame instance is flagged with "do not consume" then it always decorates its state with "have_more_data"
          after drawing.
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text, do_not_consume=True)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    element.measure(size)
    element.do_layout(size)
    element.draw(mock_canvas, region)
    assert element.state & (States.drawn | States.have_more_data)

def test_draw_multipage():
    """
    Test drawing with a mock DisplaySurface.

    REQ: If a formatted text frame instance has insufficient room to fit all the content in the passed region then it indicates that it
         has more to do by decorating the frame state with "have_more_data"
    """
    text = [
        Paragraph(in_typeface('Helvetica', "Test test"), style=normal_style),
        Paragraph(in_typeface('Helvetica', "Test paragraph2"), style=normal_style)
    ]
    size = Extent(
        Distance(10, "cm"),
        Distance(normal_style.leading, "pt")  # only leave space for one line of text to cause a page break
    )
    element = FormattedText(size, AnchorPoint.CENTER, text)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    element.measure(size)
    element.do_layout(size)
    element.draw(mock_canvas, region)
    assert element.state & (States.drawn | States.have_more_data)


def test_empty_text():
    """Test FormattedText behavior when initialized with an empty text sequence."""
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, [])
    assert bool(element) is False  # Should evaluate as False for empty content

def test_zero_extent_measurement():
    """
    Test measuring with zero extent provided.

    REQ: The formatted text measure method yield the content size when the extent passed to it is empty.
    """
    text = [Paragraph(in_typeface('Helvetica', "Test test\ntest"), style=normal_style)]
    element = FormattedText(Extent.zero, AnchorPoint.CENTER, text)
    measured_extent = element.measure(Extent.zero)
    assert measured_extent == element.content_size


def test_spacing_before_and_after():
    """
    Test getSpaceBefore and getSpaceAfter return proper values.

    REQ: formatted text & platypus integration details... need to specify?
    """
    text = [
        Paragraph(in_typeface('Helvetica', "First paragraph"), style=normal_style),
        Paragraph(in_typeface('Helvetica', "Second paragraph"), style=normal_style)
    ]
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = FormattedText(size, AnchorPoint.CENTER, text)
    assert element.getSpaceBefore() == text[0].getSpaceBefore()
    assert element.getSpaceAfter() == text[-1].getSpaceBefore()
