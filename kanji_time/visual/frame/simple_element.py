# simple_element.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Define a common operation base for layout frames that do not contain other layout frames."""
# pylint: disable=fixme

from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.protocol.content import RenderingFrame, States
from kanji_time.visual.layout.region import Pos, Region, Extent


class SimpleElement(RenderingFrame):
    """
    A frontier element on the content tree - "simple" in the sense that it has no children.

    Descendants of this class need only define a draw method for their framed content.

    Initialize a SimpleElement instance with

    :param size: the anticipated size of the rendering frame on the page.

    The SimpleElement assumes that the requested size and the final layout size are the same.
    This is not usually true - which could lead to unpleasant surprises:

    .. caution::
       The default measure and layout methods are very simple stubs.
       There is a strong chance that they will not do exactly what you want out-of-the-box.

    The default implementations of the RenderingFrame methods, however, effectively manage
    internal state variables for RenderingFrame so they should be called by any derivative
    implementations of this class.

    The class relationships for a SimpleElement instance are as follows:

    .. mermaid::
        :name: cd_simple_element
        :caption: Class relationships for a simple rendering frame.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
            class RenderingFrame {
                <<interface>>
                + begin_page(int page_number) bool
                + measure(extent: Extent) Extent
                + do_layout(target_extent: Extent) Region
                + draw(c: DisplaySurface, region: Region) None
                + state() States
            }
            class SimpleElement {
                <abstract>
                -Size _requested_size
                -Size _layout_size
                -States _state
                +begin_page(int page_number) bool
                +measure(Extent extent) Extent
                +do_layout(Extent target_extent) Region
            }
            RenderingFrame <|-- SimpleElement

    """

    def __init__(self, size: Extent):
        """Initialize a simple element with its declared size."""
        self._requested_size = size
        self._layout_size = size
        self._state = States.new

    def resize(self, new_size: Extent) -> Extent:
        """
        Mutate the requested size of the content frame.

        I cannot simply put this into the begin_page logic because I can't easily
        send a new size down to child frames in a container.
        """
        _ = new_size  # Review: ignoring a resize request for now.  Will I keep it?
        return new_size

    def begin_page(self, page_number: int):
        """
        Called by the report executor to signal that it is starting a new page.

        This stub implementation returns True the state is earlier then 'Drawn' or if we data available.
        If we return True, the state advances to 'waiting'.

        :param page_number: serial number for each page starting from 1.
        :return: page_available flag - true when there is a page waiting to be generated.
        """
        if self._state < States.drawn or States.have_more_data in self._state:
            self._state = States.waiting
            return True
        return False

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the size of the contained content.

        This stub implementation echos back the passed extent with any missing components (width/height) filled in from the requested size
        for the frame.  This return result becomes the cached _layout_size value.

        :param extent: The size of the usable area on the page - excludes margins and headers/footers.
        :return: a fully realized extent for the amount of space to allocate on the page.

        .. only:: dev_notes

            - is thread safety on self._state an issue?

        """
        self._state = States.needs_layout  # is thread safety an issue?
        self._layout_size = extent.coalesce(self.requested_size)
        return self._layout_size

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position this element at the lower-left of the parent region.

        :param extent: The size of the usable area on the page - excludes margins and headers/footers.

        :return: a private coordinate space for correctly positioning all our elements on a page.

            - region.origin = the offset into the target extent to set the coordinate origin
            - region.extent = the actual rendering size of that content.

        .. only:: dev_notes

            - is thread safety on self._state an issue?
            - docking/anchoring to position N/S/E/W or center

        """
        self._state = States.ready  # is thread safety an issue?
        self._layout_size = target_extent
        return Region(Pos(Distance.zero, Distance.zero), target_extent)


# assert issubclass(SimpleElement, RenderingFrame), "SimpleElement violates the RenderingFrame protocol!"
