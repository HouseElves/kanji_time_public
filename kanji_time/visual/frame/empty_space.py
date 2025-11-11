# empty_space.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model empty space on a page as a frame.

----

.. seealso:: :doc:`dev_notes/empty_space_notes`

----

"""

from kanji_time.visual.frame.simple_element import SimpleElement
from kanji_time.visual.layout.region import Extent, Region
from kanji_time.visual.protocol.content import DisplaySurface, States


class EmptySpace(SimpleElement):
    """
    Represent a blank area.

    Empty space is rectangular by definition.

    Initialize a blank area with the following.

    :param size: the amount of space to leave empty

    An EmptySpace has the minimal class relationships possible for a SimpleElement.

    .. mermaid::
        :name: cd_emptyspace
        :caption: Class relationships for a sized blank area frame.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
            class RenderingFrame
            class SimpleElement

            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            RenderingFrame <|-- SimpleElement
            SimpleElement <|-- EmptySpace

            class EmptySpace {
                <<realization>>
                +measure(self, Extent extent) Extent
                +draw(self, DisplaySurface c, Region region)
            }


    .. only:: dev_notes

        - the EmptySpace instance contains a "text" variable to be compatible with text layouts.
          This is a hack. Maybe force a "text client services" to add compatibility on-demand?
        - nomenclature:  size -> requested_size for parameter consistency

    """

    def __init__(self, size):
        """Initialize with the size."""
        super().__init__(size)
        self.content_size = size
        self.text = ""

    def measure(self, extent: Extent) -> Extent:  # type: ignore
        """
        Measure the minimum size of the empty space.

        :param extent: the estimated space allocated to the emptiness in the final layout.

        :return: the amount of space required to be empty.
        """
        return super().measure(self.content_size.coalesce(extent))

    def draw(self, _c: DisplaySurface, _region: Region):  # type: ignore
        """
        Render nothing at the requested location.

        This is a basic do-nothing stub.

        :param c: a ReportLab PDF canvas drawing surface
        :param region: offset + extent into the display surface for the empty space

        :return: None

        .. only:: dev_notes

            - why does this method exist?  Shouldn't it be the SimpleElement's job?

        """
        self._state = States.drawn | States.reusable
