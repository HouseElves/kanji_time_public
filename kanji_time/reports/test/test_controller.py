"""Perform coverage tests for the pagination controller and its ilk."""

import pytest
from unittest.mock import Mock, create_autospec

from kanji_time.visual.frame.page import Page
from kanji_time.visual.layout.region import Pos, Extent, Region
from kanji_time.visual.protocol.content import States, DisplaySurface
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy

from kanji_time.reports.controller import DelegatingRenderingFrame, PaginatedReport


class DummyRenderFrame:

    def __init__(self):
        self._requested_size = Extent(1, 1)
        self._layout_size = Extent(1, 1)
        self._state = States.have_more_data
        self.content_size = Extent(1, 1)
        self._region = Region(origin=Pos(0, 0), extent=Extent(1, 1))

    @property
    def state(self):
        return self._state

    @property
    def requested_size(self):
        return self._requested_size

    @property
    def layout_size(self):
        return self._layout_size

    @property
    def is_stretchy(self):
        return True

    def __bool__(self):
        return True

    def resize(self, new_size):
        self._requested_size = new_size
        return new_size

    def begin_page(self, n):
        return True

    def measure(self, extent):
        return extent

    def do_layout(self, extent):
        return self._region

    def draw(self, c, region):
        c.drew = True


def test_delegate_initialization():
    delegate = DummyRenderFrame()
    wrapper = DelegatingRenderingFrame(delegate)
    assert wrapper.state == delegate.state
    assert wrapper.layout_size == delegate.layout_size
    assert wrapper.measure(Extent(5, 5)) == Extent(5, 5)
    assert wrapper.is_stretchy
    assert wrapper.__bool__()
    assert wrapper.resize(Extent(10, 10)) == Extent(10, 10)

    mock_display = create_autospec(DisplaySurface)
    wrapper.draw(mock_display, Region(origin=Pos(0, 0), extent=Extent(1, 1)))
    mock_display.drew = True


def test_delegate_late_assignment():
    wrapper = DelegatingRenderingFrame(None)
    wrapper.set_delegatee(DummyRenderFrame())
    assert wrapper.layout_size == Extent(1, 1)


def test_paginated_report_default_begin_page_false():
    report = PaginatedReport(default_layout=({"a": DummyRenderFrame()}, Mock(spec=LayoutStrategy)))
    report.page_factory = Mock()
    report.page = Mock()
    report.page.state = set()
    assert not report.begin_page(1)


def test_paginated_report_default_begin_page_true():
    child = DummyRenderFrame()
    region = Region(origin=Pos(0, 0), extent=Extent(1, 1))

    page = Mock(spec=Page)
    page.begin_page.return_value = True
    page.state = {States.have_more_data}
    page.measure.return_value = Extent(1, 1)
    page.do_layout.return_value = region

    page_factory = Mock()
    page_factory.settings.printable_region.extent = Extent(1, 1)
    page_factory.return_value = page

    report = PaginatedReport(default_layout=({"main": child}, Mock(spec=LayoutStrategy)))
    report.page_factory = page_factory
    assert report.begin_page(1)
    page.begin_page.assert_called_once_with(1)
    page.measure.assert_called_once()
    page.do_layout.assert_called_once()


def test_paginated_report_get_page_layout_errors():
    report = PaginatedReport()
    with pytest.raises(NotImplementedError):
        report.get_page_layout("foo")


def test_paginated_report_get_page_container():
    frame = DummyRenderFrame()
    strategy = Mock(spec=LayoutStrategy)
    layout = {"main": frame}
    page = Mock(spec=Page)

    factory = Mock()
    factory.return_value = page
    factory.settings.printable_region.extent = Extent(1, 1)

    report = PaginatedReport(default_layout=(layout, strategy))
    report.page_factory = factory
    result = report.get_page_container("default_layout")
    assert result == page
    factory.assert_called_once()
