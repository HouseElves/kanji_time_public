# test_protocols.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Simple classes implementing RenderingFrame and LayoutStrategy protocols to exercise default code paths.
"""

from unittest.mock import MagicMock
from kanji_time.visual.protocol.content import RenderingFrame, States, DisplaySurface
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy
from kanji_time.visual.layout.region import Extent, Region, Pos
from kanji_time.visual.layout.distance import Distance

# Simple RenderingFrame implementation
class SimpleRenderingFrame(RenderingFrame):
    """Minimal implementation of RenderingFrame for testing default logic."""
    def __init__(self, size: Extent):
        self._requested_size = size
        self._layout_size = size
        self.content_size = size
        self._state = States.new

    def resize(self, new_size: Extent) -> Extent:  # pragma: no cover
        self._requested_size = new_size
        return new_size

    def begin_page(self, page_number: int) -> bool:
        if self._state < States.drawn:
            self._state = States.waiting
            return True
        return False

    def measure(self, extent: Extent) -> Extent:
        self._layout_size = extent or self._requested_size
        self._state = States.needs_layout
        return self._layout_size

    def do_layout(self, target_extent: Extent) -> Region:
        self._layout_size = target_extent
        self._state = States.ready
        return Region(Pos(Distance(0, "cm"), Distance(0, "cm")), target_extent)

    def draw(self, c: DisplaySurface, region: Region) -> None:
        self._state = States.drawn | States.reusable

# Basic LayoutStrategy implementation
class BasicLayoutStrategy(LayoutStrategy):
    """Minimal implementation of LayoutStrategy for default testing."""
    def measure(self, element_extents: list[Extent], fit_elements: Extent) -> Extent:
        total_width = max(extent.width for extent in element_extents) if element_extents else Distance.zero
        total_height = sum(extent.height for extent in element_extents)
        return Extent(total_width, total_height)

    def layout(self, target_extent: Extent, element_extents: list[Extent], fit_elements: Extent) -> tuple[Extent, list[Region]]:
        regions = []
        current_y = Distance.zero
        for extent in element_extents:
            region = Region(
                Pos(Distance.zero, current_y),
                Extent(extent.width, extent.height)
            )
            regions.append(region)
            current_y += extent.height
        return (Extent(target_extent.width, current_y), regions)

# TEST CASES
def test_simple_rendering_frame():
    """Test SimpleRenderingFrame lifecycle."""
    frame = SimpleRenderingFrame(Extent(Distance(10, "cm"), Distance(5, "cm")))
    assert not bool(frame)
    assert not frame.is_stretchy.width
    assert not frame.is_stretchy.height
    assert frame.state == States.new
    frame.begin_page(1)
    assert frame.state == States.waiting
    frame.measure(Extent(Distance(12, "cm"), Distance(6, "cm")))
    assert frame.state == States.needs_layout
    frame.do_layout(Extent(Distance(12, "cm"), Distance(6, "cm")))
    assert frame.state == States.ready
    mock_canvas = MagicMock()
    frame.draw(mock_canvas, Region(Pos(Distance(0, "cm"), Distance(0, "cm")), frame.layout_size))
    assert frame.state == (States.drawn | States.reusable)
    next_page_ready = frame.begin_page(2)
    assert not next_page_ready


def test_basic_layout_strategy():
    """Test BasicLayoutStrategy layout and measurement."""
    strategy = BasicLayoutStrategy()
    elements = [
        Extent(Distance(5, "cm"), Distance(2, "cm")),
        Extent(Distance(5, "cm"), Distance(3, "cm")),
        Extent(Distance(5, "cm"), Distance(4, "cm"))
    ]
    measured_extent = strategy.measure(elements, Extent.zero)
    assert measured_extent == Extent(Distance(5, "cm"), Distance(9, "cm"))
    target_extent = Extent(Distance(10, "cm"), Distance(10, "cm"))
    layout_extent, regions = strategy.layout(target_extent, elements, Extent.zero)
    assert layout_extent.height == Distance(9, "cm")
    assert len(regions) == 3
    assert regions[0].extent == Extent(Distance(5, "cm"), Distance(2, "cm"))
    assert regions[1].extent == Extent(Distance(5, "cm"), Distance(3, "cm"))
    assert regions[2].extent == Extent(Distance(5, "cm"), Distance(4, "cm"))
