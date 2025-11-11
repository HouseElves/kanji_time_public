# test_remaining_.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Test suite for EmptySpace, globals, Page, and HorizontalRule classes with full branch coverage.
"""

import pytest
from unittest.mock import MagicMock
from reportlab.lib.colors import black, blue
from reportlab.lib.pagesizes import LETTER, landscape
from kanji_time.visual.frame.empty_space import EmptySpace
from kanji_time.visual.frame.page_rule import HorizontalRule
from kanji_time.visual.frame.page import Page, SETTINGS, Margins
from kanji_time.visual.layout.region import Extent, Region, Pos
from kanji_time.visual.layout.distance import Distance, distance_list
from kanji_time.visual.protocol.content import States
from kanji_time.visual.frame.test.test_container import create_mock_layout_strategy, create_mock_child


# Empty Space Tests ------------------------------------------------------------------------------------------------------------------------ #


def test_empty_space_initialization():
    """
    Test initializing EmptySpace with given size.

    REQ: An empty space type must be instantiated with distances for the width and height to leave empty.
    """
    size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    space = EmptySpace(size)
    assert space.content_size == size


def test_empty_space_measure():
    """
    Test measuring EmptySpace returns the correct size.

    REQ: Measuring an empty space instance yields back the width and height with which it was instantiated.
    """
    size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    space = EmptySpace(size)
    measured_extent = space.measure(size)
    assert measured_extent == size


def test_empty_space_draw():
    """
    Test drawing EmptySpace does nothing but updates state.

    REQ: Drawing an empty space instance does nothing except advance its state to "drawn, reusable".
    """
    size = Extent(Distance(5, "cm"), Distance(5, "cm"))
    space = EmptySpace(size)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    space.draw(mock_canvas, region)
    assert space.state == (States.drawn | States.reusable)


# Page Tests ------------------------------------------------------------------------------------------------------------------------------- #


def test_page_initialization():
    """
    Test Page initialization with paper size, orientation, and margins.

    REQ: The page type must be instantiated by providing a paper size, orientation, and margins arguments.
    """
    margins = Margins(
        *distance_list(1, 1, 1, 1, unit="in")
    )
    page = Page(
        paper=SETTINGS.paper,
        orientation=SETTINGS.orientation,
        margins=margins,
        element_name="TestPage",
        child_elements={},
        layout_strategy=MagicMock()
    )
    expected_size = SETTINGS.orientation(SETTINGS.paper.value)
    assert page.page_size == Extent(*map(lambda x: Distance(x, "pt"), expected_size))


def test_page_printable_region():
    """
    Test the printable region excluding margins.

    REQ: The page type has a requested size property that coincides with the usable extent of the paper.
    """
    margins = Margins(
        Distance(1, "in"), Distance(1, "in"), Distance(1, "in"), Distance(1, "in")
    )
    page = Page(
        paper=SETTINGS.paper,
        orientation=SETTINGS.orientation,
        margins=margins,
        element_name="TestPage",
        child_elements={},
        layout_strategy=create_mock_layout_strategy()
    )
    assert page.page_size.width > page.requested_size.width
    assert page.page_size.height > page.requested_size.height


def test_page_factory():
    """
    Test creating pages using the factory method.

    REQ: The page type provides a factory creation method that yields a page factory to create page instances using page settings frozen as
         at the time this factory creation method is called.
    """
    child_elements = {
        "child1": create_mock_child(),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    factory = Page.factory()
    page_container = factory(
        element_name="Test page_container",
        child_elements=child_elements,
        layout_strategy=layout_strategy
    )
    assert isinstance(page_container, Page)
    assert page_container.element_name == "Test page_container"
    assert page_container.layout_strategy == layout_strategy
    assert len(page_container.child_elements) == 2
    assert factory.settings.printable_region.extent == page_container.requested_size
    assert factory.settings.printable_region.extent in factory.settings.page_size


# Horizontal Rule Tests -------------------------------------------------------------------------------------------------------------------- #


def test_horizontal_rule_initialization():
    """
    Test initializing HorizontalRule with size and color.

    REQ: A horizontal rule type must be instantiated with an extent for the width and height and a color for the rule.
    """
    size = Extent(Distance(10, "cm"), Distance(0.5, "cm"))
    rule = HorizontalRule(size, blue)
    assert rule.content_size == size
    assert rule.color == blue


def test_horizontal_rule_measure():
    """
    Test measuring HorizontalRule returns the correct size.

    REQ: Measuring a horizontal rule instance yields back the width and height with which it was instantiated.
    """
    size = Extent(Distance(10, "cm"), Distance(0.5, "cm"))
    rule = HorizontalRule(size, blue)
    measured_extent = rule.measure(size)
    assert measured_extent == size


def test_horizontal_rule_draw():
    """
    Test drawing HorizontalRule draws a line on canvas.

    REQ: Drawing a horizontal rule instance results in the rule drawn on the passed display surface centered in the passed region instance
         and the state advanced to "drawn, reusable".
    REQ: A horizontal rule is clipped to the print area of the page when it is drawn.
    """
    size = Extent(Distance(10, "cm"), Distance(0.5, "cm"))
    rule = HorizontalRule(size, black)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    rule.draw(mock_canvas, region)
    mock_canvas.setLineWidth.assert_called_once_with(size.height.pt)
    mock_canvas.setStrokeColor.assert_called_once_with(black)
    mock_canvas.line.assert_called_once()
    assert rule.state == (States.drawn | States.reusable)
