"""Test suite, with full branch coverage, for a rendering frame containing a ReportLab drawing class instance."""

import pytest
from unittest.mock import MagicMock, patch
from kanji_time.visual.frame.drawing import ReportLabDrawing
from kanji_time.visual.layout.region import Extent, Region, Pos
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.protocol.content import States
from kanji_time.adapter.svg import RLDrawing


# ReportLab Drawing Tests ------------------------------------------------------------------------------------------------------------------ #


def create_mock_drawing(bounds=(0, 0, Distance(1, "cm").pt, Distance(2, "cm").pt)):
    """Helper to create a mock RLDrawing with specific bounds."""
    mock_drawing = MagicMock(spec=RLDrawing)
    mock_drawing.getBounds.return_value = bounds
    mock_drawing.renderScale = 1.0  # Add missing attribute to avoid AttributeError
    return mock_drawing


def test_drawing_initialization():
    """
    Test initializing a ReportLabDrawing instance.

    REQ: A report lab drawing frame type must be instantiated with an extent instance for its requested size, an anchor point in its parent,
         and report lab drawing instance that holds its content.
    REQ: A report lab drawing frame instance exposes its initialization parameters through like-named properties.
    REQ: After initialization, a report lab drawing frame instance is in the "new" state.
    """
    drawing = create_mock_drawing()
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    assert element.drawing == drawing
    assert element.anchor == AnchorPoint.CENTER
    assert element.requested_size == size
    assert element.state == States.new


def test_measure_with_drawing():
    """
    Test measure calculates content size from drawing bounds.

    REQ: The report lab drawing type implements a "measure" method from the rendering frame protocol that yields the actual extent required
         for its framed content including whitespace padding.
    REQ: The report lab drawing type's measure method must yield an extent at least as large as the originally requested size.
    """
    drawing = create_mock_drawing((0, 0, 100, 200))
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    measured_extent = element.measure(size)
    assert measured_extent.width >= Distance(100, "pt")
    assert measured_extent.height >= Distance(200, "pt")
    assert element.state == States.needs_layout

def test_measure_without_drawing():
    """
    Test measure falls back to minimum size when drawing is None.

    REQ: The report lab drawing type's "measure" method must yield an extent exactly as large as the originally requested size when it has no
         drawing content.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, None)  # type: ignore
    measured_extent = element.measure(size)
    assert measured_extent == size


def test_zero_extent_measurement():
    """
    Test measuring with zero extent.

    REQ: The report lab drawing type's "measure" method must yield an extent exactly as large as the drawing content when it has no
         requested size.
    """
    drawing = create_mock_drawing()
    element = ReportLabDrawing(Extent.zero, AnchorPoint.CENTER, drawing)
    measured_extent = element.measure(Extent.zero)
    assert measured_extent == element.content_size


def test_do_layout():
    """
    Test layout positions the drawing correctly in target extent.

    REQ: The report lab drawing type implements a "do layout" method from the rendering frame protocol that yields a region of the same size
         as the target extent and an origin that positions the drawing content in that region according to the frame's anchor point.
    """
    drawing = create_mock_drawing((0, 0, 100, 200))
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    target_extent = Extent(Distance(20, "cm"), Distance(20, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    element.measure(size)
    region = element.do_layout(target_extent)
    assert region.origin.x >= Distance.zero
    assert region.origin.y >= Distance.zero
    assert element.state == States.ready


def test_do_layout_with_insufficient_space():
    """
    Test layout raises an error when space is insufficient.

    REQ: The report lab drawing type's "measure" method yields a value error exception when the passed target extent is too small to hold
         the drawing.
    """
    drawing = create_mock_drawing((0, 0, 100, 200))
    size = Extent(Distance(5, "cm"), Distance(2, "cm"))
    small_extent = Extent(Distance(5, "cm"), Distance(2, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    element.measure(size)
    with pytest.raises(ValueError):
        element.do_layout(small_extent)


def test_draw():
    """
    Test drawing renders correctly on a mocked canvas.

    TODO:  how can I inspect the output?  I guess a known PDF binary?

    REQ: Drawing a report lab drawing frame instance faithfully renders the drawing content positioned in the passed region.
    """
    drawing = create_mock_drawing()
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    element.measure(size)
    element.do_layout(size)
    element.draw(mock_canvas, region)
    assert element.state & States.drawn
    drawing.getBounds.assert_called_once()


def test_negative_bounds():
    """
    Test handling drawing with negative bounds.

    REQ: Negative values in a report lab drawing content are interpreted relative to the origin of the region passed to the "draw" method.
    """
    drawing = create_mock_drawing((-50, -50, 50, 50))
    size = Extent(Distance(10, "pt"), Distance(5, "pt"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, drawing)
    measured_extent = element.measure(size)
    assert measured_extent.width == Distance(100, "pt")
    assert measured_extent.height == Distance(100, "pt")


def test_draw_no_drawing():
    """
    Test drawing when the drawing attribute is None.

    REQ: Drawing a report lab drawing frame instance that has no drawing content causes a warning to be sent to the log.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ReportLabDrawing(size, AnchorPoint.CENTER, None)  # type: ignore
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    element.measure(size)
    element.do_layout(size)
    with patch('visual.frame.drawing.logging.warning') as mock_warning:
        element.draw(mock_canvas, region)
        mock_warning.assert_called_once_with("no diagram to draw!")
