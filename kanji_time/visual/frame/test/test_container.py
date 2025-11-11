# test_container.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Test suite for Container class with full branch coverage.
"""

import pytest
from unittest.mock import MagicMock
from kanji_time.visual.frame.container import Container
from kanji_time.visual.layout.region import Extent, Region, Pos
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.protocol.content import States, RenderingFrame
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy


# MOCK Setup ------------------------------------------------------------------------------------------------------------------------------- #


def create_mock_child(state=States.ready, stretchy_width=False, stretchy_height=False, data_state=States.new):
    """Helper to create a mock child RenderingFrame."""
    mock_child = MagicMock(spec=RenderingFrame)
    mock_child.measure.return_value = Extent(Distance(10, "cm"), Distance(5, "cm"))
    mock_child.state = state

    def measure_side_effect(*args, **kwargs):
        """Transition state to needs_layout upon measure call."""
        mock_child.state = States.needs_layout
        return Extent(Distance(10, "cm"), Distance(5, "cm"))

    mock_child.measure.side_effect = measure_side_effect

    def draw_side_effect(*args, **kwargs):
        """Transition state to drawn upon measure call."""
        mock_child.state = States.drawn | data_state
    mock_child.draw.side_effect = draw_side_effect

    def do_layout_side_effect(*args, **kwargs):
        """Transition state to ready upon do_layout call."""
        mock_child.state = States.ready
        return Region(Pos(Distance(0, "cm"), Distance(0, "cm")), Extent(Distance(20, "cm"), Distance(10, "cm")))

    mock_child.do_layout.side_effect = do_layout_side_effect


    mock_child.is_stretchy = MagicMock(width=stretchy_width, height=stretchy_height)
    mock_child.do_layout.return_value = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), Extent(Distance(10, "cm"), Distance(5, "cm")))
    return mock_child

def create_mock_layout_strategy(stretchy: bool = False):
    """Helper to create a mock LayoutStrategy."""
    mock_strategy = MagicMock(spec=LayoutStrategy)
    mock_strategy.measure.return_value = Extent(Distance(20 + 10*(int(stretchy)), "cm"), Distance(10 + 5*int(stretchy), "cm"))

    # Set return_value directly since MagicMock instances are callable by default
    mock_strategy.layout.return_value = (
        Extent(Distance(20 + 10*(int(stretchy)), "cm"), Distance(10 + 5*int(stretchy), "cm")),
        [
            Region(
                Pos(Distance(0, "cm"), Distance(0, "cm")),
                Extent(Distance(10 + 10*int(stretchy), "cm"), Distance(5 + 5*int(stretchy), "cm"))
            ),
            Region(Pos(Distance(10, "cm"), Distance(0, "cm")), Extent(Distance(10, "cm"), Distance(5, "cm")))
        ]
    )
    return mock_strategy


# Content Frame Container Frame Tests ------------------------------------------------------------------------------------------------------ #


def test_container_initialization():
    """
    Test initializing a Container instance with child elements.

    REQ: A container frame type must be instantiated with a name for the container, extent instance for its requested size, a dictionary of
         child rendering frame instances, and a layout strategy instance.
    REQ: A container frame instance exposes its initialization parameters through like-named properties.
    REQ: After initialization, a container frame instance is in the "new" state.
    """
    child_elements = {
        "child1": create_mock_child(),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("TestContainer", size, child_elements, layout_strategy)
    assert container.element_name == "TestContainer"
    assert container.layout_strategy == layout_strategy
    assert len(container.child_elements) == 2


def test_child_elements_immutable():
    """
    Test immutability of child_elements property.

    REQ: The "child elements" property of a container frame instance is immutable - attempting to change any member of it
         yields a type error exception.
    """
    child_elements = {"child1": create_mock_child()}
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("ImmutableTest", size, child_elements, layout_strategy)
    with pytest.raises(TypeError):
        container.child_elements["child2"] = create_mock_child()  # type: ignore


def test_measure_children():
    """
    Test measuring all child elements.

    REQ: The container frame type's "measure" method defers to its layout strategy to measure its content.
    """
    child_elements = {
        "child1": create_mock_child(),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("MeasureTest", size, child_elements, layout_strategy)
    measured_extent = container.measure(size)
    assert measured_extent == size
    assert container.state == States.needs_layout


def test_stretchy_child_measurement():
    """
    Test measuring stretchy child elements.

    REQ: The container frame type's "measure" method ignores dimensions marked as "fit to" on its children.
    """
    child_elements = {
        "child1": create_mock_child(stretchy_width=True),
        "child2": create_mock_child(stretchy_height=True)
    }
    layout_strategy = create_mock_layout_strategy(stretchy=True)
    size = Extent(Distance(30, "cm"), Distance(15, "cm"))
    container = Container("StretchTest", size, child_elements, layout_strategy)
    measured_extent = container.measure(size)
    assert measured_extent.width == Distance(30, "cm")
    assert measured_extent.height == Distance(15, "cm")


def test_layout_allocation():
    """
    Test layout region allocation with valid child elements.

    TODO: some easily testable dummy strategies w/ fit to behavior -> single origin stack (overlap), step origin (partial overlap), diagonal

    REQ: The container frame type's "do_layout" method defers to its layout strategy to lay out its content.
    """
    child_elements = {
        "child1": create_mock_child(),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("LayoutTest", size, child_elements, layout_strategy)
    container.measure(size)
    region = container.do_layout(size)
    assert region.extent == size
    assert container.state == States.ready


def test_draw_container():
    """
    Test drawing child elements inside container.

    REQ: The container frame type's "draw" method defers to each child to draw itself in the region that it laid out.
    """
    child_elements = {
        "child1": create_mock_child(),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("DrawTest", size, child_elements, layout_strategy)
    container.measure(size)
    container.do_layout(size)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    container.draw(mock_canvas, region)
    assert container.state == States.drawn


def test_draw_onepage_data():
    """Test drawing child elements inside container."""
    child_elements = {
        "child1": create_mock_child(data_state=States.all_data_consumed),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("DrawTest", size, child_elements, layout_strategy)
    container.measure(size)
    container.do_layout(size)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    container.draw(mock_canvas, region)
    assert container.state == States.drawn | States.all_data_consumed
    new_page_waiting = container.begin_page(2)
    assert not new_page_waiting
    assert container.state == States.drawn | States.all_data_consumed


def test_draw_multipage_data():
    """Test drawing child elements inside container."""
    child_elements = {
        "child1": create_mock_child(data_state=States.have_more_data),
        "child2": create_mock_child()
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("DrawTest", size, child_elements, layout_strategy)
    container.measure(size)
    container.do_layout(size)
    mock_canvas = MagicMock()
    region = Region(Pos(Distance(0, "cm"), Distance(0, "cm")), size)
    container.draw(mock_canvas, region)
    assert container.state == States.drawn | States.have_more_data
    new_page_waiting = container.begin_page(2)
    assert new_page_waiting
    assert container._state == States.waiting


def test_state_aggregation():
    """
    Test state aggregation reflects child states.

    REQ: The state of a container instance is the most advanced state of all of its children.
    REQ: A container instance's state is decorated with "reusable" if any of its children's state is.
    REQ: A container instance's state is decorated with "have_more_data" if any of its children's state is.
    REQ: A container instance's state is decorated with "all_data_consumed if no child is decorated with "have more data" and any child is
         decorated with "all_data_consumed"
    """
    child_elements = {
        "child1": create_mock_child(state=States.drawn | States.reusable),
        "child2": create_mock_child(state=States.drawn | States.have_more_data)
    }
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("StateTest", size, child_elements, layout_strategy)
    state = container.state
    assert state & States.have_more_data
    assert state & States.reusable


def test_no_child_elements():
    """
    Test container with no child elements.

    REQ:  Measuring an empty container yields its requested size.
    """
    layout_strategy = create_mock_layout_strategy()
    size = Extent(Distance(20, "cm"), Distance(10, "cm"))
    container = Container("EmptyTest", size, {}, layout_strategy)
    measured_extent = container.measure(size)
    assert measured_extent == size
    assert container.state == States.needs_layout


# def test_child_elements_exceed_space():
#     """Test child elements that collectively exceed available space."""
#     child_elements = {
#         "child1": create_mock_child(),
#         "child2": create_mock_child()
#     }
#     layout_strategy = create_mock_layout_strategy()
#     size = Extent(Distance(10, "cm"), Distance(5, "cm"))  # Smaller space
#     container = Container("ExceedTest", size, child_elements, layout_strategy)
#     with pytest.raises(ValueError):
#         container.measure(size)


def test_update_add_new_frame():
    """
    REQ: The `update()` method adds new frames if not already present in the layout.
    """
    layout_strategy = create_mock_layout_strategy()
    container = Container("UpdateAdd", Extent(Distance(20, "cm"), Distance(10, "cm")), {}, layout_strategy)

    new_frame = create_mock_child()
    updated = container.update({"new": new_frame})

    assert "new" in updated
    assert updated["new"] is new_frame


def test_update_replace_existing_frame():
    """
    REQ: The `update()` method replaces an existing frame if the instance is different.
    """
    original_frame = create_mock_child()
    replacement_frame = create_mock_child()

    layout_strategy = create_mock_layout_strategy()
    container = Container("UpdateReplace", Extent(Distance(20, "cm"), Distance(10, "cm")),
                          {"frame": original_frame}, layout_strategy)

    updated = container.update({"frame": replacement_frame})

    assert "frame" in updated
    assert updated["frame"] is replacement_frame


def test_update_ignores_identical_instance():
    """
    REQ: The `update()` method preserves the existing instance if it is the same.
    """
    frame = create_mock_child()
    layout_strategy = create_mock_layout_strategy()
    container = Container("UpdateSame", Extent(Distance(20, "cm"), Distance(10, "cm")),
                          {"frame": frame}, layout_strategy)

    updated = container.update({"frame": frame})

    # Ensure no layout entry was regenerated
    assert "frame" in updated
    assert updated["frame"] is frame


def test_update_removes_named_frame():
    """
    REQ: The `update()` method removes a named frame if its value is None.
    """
    frame = create_mock_child()
    layout_strategy = create_mock_layout_strategy()
    container = Container("UpdateRemove", Extent(Distance(20, "cm"), Distance(10, "cm")),
                          {"delete_me": frame}, layout_strategy)

    updated = container.update({"delete_me": None})

    assert "delete_me" not in updated


def test_update_combined_add_remove():
    """
    REQ: The `update()` method supports simultaneous add/remove operations.
    """
    keep = create_mock_child()
    remove = create_mock_child()
    layout_strategy = create_mock_layout_strategy()
    container = Container("UpdateMixed", Extent(Distance(20, "cm"), Distance(10, "cm")),
                          {"remove_me": remove, "keep_me": keep}, layout_strategy)

    new = create_mock_child()
    updated = container.update({"remove_me": None, "new_frame": new})

    assert "remove_me" not in updated
    assert "keep_me" in updated
    assert "new_frame" in updated
