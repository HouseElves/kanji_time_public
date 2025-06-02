"""Test suite for a stack layout strategy."""

import pytest
from kanji_time.visual.layout.stack_layout import StackLayoutStrategy
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent


#: .. todo:: pytest fixtures


# Stack Layout Tests ----------------------------------------------------------------------------------------------------------------------- #


def test_bogus_stack_layout():
    """
    Confirm only horizontal and vertical stack layouts.

    REQ: A stack layout type may only be instantiated with "horizontal" or "vertical" - other arguments yield a value error exception.
    """
    with pytest.raises(ValueError):
        _ = StackLayoutStrategy("diagonal")


def test_vertical_stack_layout():
    """
    Confirm vertical stack layouts.

    REQ: A stack layout type instance set to vertical measures the height of a passed list of extents as the sum of their heights
         and the width as the max of their widths.
    REQ: A stack layout type instance ignores "fit to" distances when measuring a passed list of extents.
    REQ: A stack layout type instance set to vertical defaults height "fit to" distances to zero while laying out a passed list of extents
         when the passed a maximum height argument is less than or equal to the measured height of the extents.
    REQ: A stack layout type instance set to vertical distributes excess height evenly among all the extents with a height of "fit to"
         when the passed a maximum height argument is greater the measured height of the extents
    """

    extents = [
        Extent(Distance.parse("100pt"), Distance.parse("110pt")),
        Extent(Distance.parse("*"), Distance.parse("220pt")),
        Extent(Distance.parse("300pt"), Distance.parse("330pt")),
        Extent(Distance.parse("400pt"), Distance.parse("*")),
    ]
    fit_to_test = Extent([1], [3])

    vlayout = StackLayoutStrategy("vertical")
    vertical_size = vlayout.measure(extents, fit_to_test)
    assert vertical_size == Extent(Distance.parse("400pt"), Distance.parse("660pt")), f"Unexpected vertical size = {vertical_size}."

    consumed, vertical_regions = vlayout.layout(vertical_size, extents, fit_to_test)
    assert consumed == vertical_size
    assert vertical_regions[3].extent.height.pt == 0

    consumed, vertical_regions = vlayout.layout(2*vertical_size, extents, fit_to_test)
    assert consumed == 2*vertical_size
    assert vertical_regions[3].extent.height.pt == vertical_size.height.pt


def test_horizontal_stack_layout():
    """
    Confirm horizontal stack layouts.

    REQ: A stack layout type instance set to horizontal measures the width of a passed list of extents as the sum of their widths
         and the height as the max of their height.
    REQ: A stack layout type instance ignores "fit to" distances when measuring a passed list of extents.
    REQ: A stack layout type instance set to horizontal defaults width "fit to" distances to zero while laying out a passed list of extents
         when the passed a maximum width argument is less than or equal to the measured width of the extents.
    REQ: A stack layout type instance set to horizontal distributes excess width evenly among all the extents with a width of "fit to"
         when the passed a maximum width argument is greater the measured width of the extents
    """

    extents = [
        Extent(Distance.parse("100pt"), Distance.parse("110pt")),
        Extent(Distance.parse("*"), Distance.parse("220pt")),
        Extent(Distance.parse("300pt"), Distance.parse("330pt")),
        Extent(Distance.parse("400pt"), Distance.parse("*")),
    ]
    fit_to_test = Extent([1], [3])

    hlayout = StackLayoutStrategy("horizontal")
    horizontal_size = hlayout.measure(extents, fit_to_test)
    assert horizontal_size == Extent(Distance.parse("800pt"), Distance.parse("330pt")), f"Unexpected horizontal size = {horizontal_size}."
    consumed, horizontal_regions = hlayout.layout(horizontal_size, extents, fit_to_test)
    assert consumed == horizontal_size
    assert horizontal_regions[1].extent.width.pt == 0
    consumed, horizontal_regions = hlayout.layout(2*horizontal_size, extents, fit_to_test)
    assert consumed == 2*horizontal_size
    assert horizontal_regions[1].extent.width.pt == horizontal_size.width.pt
