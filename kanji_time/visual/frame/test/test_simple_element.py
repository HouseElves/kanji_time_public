# test_simple_element.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Test suite for SimpleElement class with full branch coverage.
"""

from kanji_time.visual.frame.simple_element import SimpleElement
from kanji_time.visual.layout.region import Extent, Pos
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.protocol.content import States


class ImplementSimpleElement(SimpleElement):
    """Stub class for testing the SimpleElement base class."""

    def __init__(self, size):
        """Provide the 'content' data member required by the RenderingFrame protocol."""
        super().__init__(size)
        self.content_size = size

    def draw(self, c, region):
        """Provide a stub draw method required by the RenderingFrame protocol."""
        return  # pragma: no cover


# Simple Element Tests --------------------------------------------------------------------------------------------------------------------- #


def test_simple_element_initialization():
    """
    Test initialization of SimpleElement with a given size.

    REQ: A simple type must be instantiated with an extent instance for its requested size.
    REQ: After initialization, a simple type instance is in the "new" state.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ImplementSimpleElement(size)
    assert element.requested_size == size
    assert element._layout_size == size
    assert element.state == States.new


def test_simple_element_resize():
    """
    Test resizing the SimpleElement, even though the method currently ignores the new size.

    REQ: Resizing a simple element instance is not currently implemented since it is of dubious value.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    new_size = Extent(Distance(15, "cm"), Distance(7, "cm"))
    element = ImplementSimpleElement(size)
    resized = element.resize(new_size)
    assert resized == new_size  # Verify the return value, even though the internal size isn't changed.


def test_begin_page_initial_state():
    """
    Test begin_page starts correctly when state is less than drawn.

    REQ: The simple element type provides a begin_page() method that can be called on an instance any time before the page is drawn or
         after it is drawn and there is more data available to draw.
    REQ: After successfully beginning a page, a simple type instance is in the "waiting" state.
    REQ: If the client calls begin_page() multiple times for simple element instance before drawing it then any cached measurement
         or layout data for the instance must be discarded.

    TODO: "waiting, fresh data" vs "waiting, reusing data" states.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ImplementSimpleElement(size)
    assert element.begin_page(1) is True
    assert element.state == States.waiting

def test_begin_page_with_data():
    """
    Test begin_page when element has more data.

    REQ: The simple element type provides a begin_page() method that can be called on an instance any time before the page is drawn or
         after it is drawn and there is more data available to draw.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ImplementSimpleElement(size)
    element._state = States.have_more_data
    assert element.begin_page(1) is True
    assert element.state == States.waiting

def test_begin_page_drawn_state():
    """
    Test begin_page returns False if already drawn and no more data.

    REQ: The simple element's begin page method yield False if the simple element instance has nothing left for it to do: it's been drawn
         and there is no more data available.
    """
    size = Extent(Distance(10, "cm"), Distance(5, "cm"))
    element = ImplementSimpleElement(size)
    element._state = States.drawn
    assert element.begin_page(1) is False


def test_measure_coalesce():
    """
    Test measure method coalesces requested and provided extents.

    REQ: The simple element type provides a limited default measure method that echoes back the passed extent coalesced with the instance's
         requested size.
    REQ: After measuring, a simple type instance is in the "needs layout" state.
    """
    initial_size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    input_extent = Extent(Distance(10, "cm"), Distance(0, "cm"))
    element = ImplementSimpleElement(initial_size)
    measured_extent = element.measure(input_extent)
    assert measured_extent == element.layout_size
    assert measured_extent.width == Distance(10, "cm")
    assert measured_extent.height == Distance(5, "cm")  # Coalesced height
    assert element.state == States.needs_layout


def test_measure_with_zero_extent():
    """
    Test measure with an extent of zero dimensions.

    REQ: The simple element type provides a limited default measure method that echoes back the passed extent coalesced with the instance's
         requested size.
    """
    initial_size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    input_extent = Extent(Distance.zero, Distance.zero)
    element = ImplementSimpleElement(initial_size)
    measured_extent = element.measure(input_extent)
    assert measured_extent == initial_size  # Should fall back to the requested size


def test_do_layout():
    """
    Test do_layout positions element correctly in the parent region.

    REQ: The simple element type provides a limited default layout method that echoes back the the target extent in a region with zero origin.
    """
    initial_size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    target_extent = Extent(Distance(10, "cm"), Distance(10, "cm"))
    element = ImplementSimpleElement(initial_size)
    region = element.do_layout(target_extent)
    assert region.origin == Pos(Distance.zero, Distance.zero)
    assert region.extent == target_extent
    assert element.state == States.ready
