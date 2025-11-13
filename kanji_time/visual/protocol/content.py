# content.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Define a common interface for sized and renderable report content.

The underlying concept is that all drawable elements must support a common method interface as follows:

    - measure() to provide the minimum size for the element (and any children, if present).
    - layout() to position itself (and any children) inside some area and set up a local coordinate system for drawing.
    - draw() to execute technology-specific instructions to render the drawable element

A particular implementation of a RenderingFrame knows how to draw one specific type of content: a drawing, text, etc.

The overall vision is that a particular rendering technology provides adapters for known standard RenderingFrame implementations
that either replace the implementation outright or tweak the well-known output format of a frame to suit its needs.

    - We're not quite there on this vision yet -- Kanji Time is highly dependant on ReportLab for PDF output right now.
      I'm striving to keep technology and semantics decoupled - but this is an ideal.

.. only:: dev_notes

    .. seealso:: :doc:`dev_notes/content_notes`

----

"""
# pylint: disable=fixme

from typing import Protocol, runtime_checkable
import enum

from reportlab.pdfgen import canvas

from kanji_time.visual.layout.region import Region, Extent


class DisplaySurface(canvas.Canvas):  # pylint: disable=abstract-method
    """
    Model a surface on which something can be rendered.

    .. only:: dev_notes

        - a DisplaySurface is explicitly a ReportLab PDF canvas right now.  This is a placeholder for a future generic protocol.
        - Move DisplaySurface into the technology agnostic layers

    """
    ...


class States(enum.IntFlag):
    """
    Encapsulate the processing state of a content frame.

    The normal progression is
        new -> waiting -> needs_layout -> ready -> drawn

    A content frame always starts life in the 'new' state.

        - Calling "begin_page" usually sends it to the 'waiting' state from 'new' or 'drawn'.
          but could send it all the way to 'ready' if there's no measurement or layout to do.
        - Calling "measure" sends it to the 'needs_layout' or 'ready' state.
        - Calling "do_layout" sends it to the 'ready' state from 'needs_layout'
        - Calling "draw" always sends it to the 'drawn' state from 'ready'
          (unless there's an error of some kind and we can recover.)

    The drawn state my be decorated with

        - have_more_data - to indicate another page of content is available
        - reusable - to indicate that the same content can be drawn again
        - all_data_consumed - to indicate that there's nothing left to draw

    These decorator flags govern which frames appear on the next page of output.

    .. only:: dev_notes

        - think about "def ready_for(States.some_state) -> bool" to check if we are able to transit to some_state
        - think about "with next_state(States.some_state):" that

            - verifies that I can enter some_state,
            - verifies that the operations in the context, and,
            - keeps thread safety.

        - Consider something like a StateService mix-in that exposes a "next_state" context & is initialized with an enum and verifier
          functions that inspect 'self' data to determine "in_state" and "ready_for_transition"; maybe also "state_from_self".
          Really, "state_from_self" would end up as the core function that drives "in_state" and the "start_transition" exit function
          that determines success.

    """
    # pylint: disable=invalid-name
    new = 0
    waiting = 1
    needs_layout = 2
    ready = 4
    drawing = 8
    drawn= 16
    have_more_data = 32
    reusable = 64
    all_data_consumed = 128
    finished = 16 | 32 | 64 | 128


@runtime_checkable
class RenderingFrame(Protocol):
    """
    Model a measured and drawable section of report content.

    The RenderingFrame is the core interface between the layout engine and any drawable element.

    Key Design Considerations
    -------------------------

    1. All layout-aware renderable objects — including both leaf and container nodes — implement this protocol.

    The intended design goal is to encapsulate all spatial negotiation, measurement, and rendering behaviors in a single object.
    This interface hides internal content representation from the layout engine.

    2. A layout algorithm receives ContentFrame instances opaque units. It only sees:

        - How large a frame wants to be (`requested_size`)
        - How large it actually is after layout (`layout_size`)
        - Whether it has more content for pagination (`States.have_more_data`)

    Every ContentFrame is (and must be) self-contained and self-managing. It may be composite or atomic, stretchable or fixed-size.
    It may render into any subregion it declares via `do_layout`.

    3. This interface serves as the polymorphic contract for all drawable elements in a layout tree.

    """

    _requested_size: Extent
    _layout_size: Extent
    content_size: Extent
    _state: States

    @property
    def state(self) -> States:
        """Produce the current state of the content frame."""
        return self._state

    @property
    def requested_size(self) -> Extent:
        """Yield the requested space to reserve for the framed content."""
        # Extent.coalesce(dim) or coalesce(width, height) - Extent can be 0 and non-zero in each dim
        return self._requested_size or Extent.fit_to  # why  not do this coalesce up front?

    @property
    def layout_size(self) -> Extent:
        """Yield the actual space (as computed during measure()) occupied by the framed content for layout."""
        assert self.state >= States.needs_layout
        return self._layout_size

    @property
    def is_stretchy(self) -> Extent:
        """Produce true if this content can be fit to some dimensions (linearly upward only)."""
        return Extent(
            self.requested_size is not None and (self.requested_size.width.at_least or self.requested_size.width.unit == "*"),
            self.requested_size is not None and (self.requested_size.height.at_least or self.requested_size.height.unit == "*")
        )

    def __bool__(self) -> bool:
        """Produce true when this rendering frame has non-trivial content."""
        return False

    def resize(self, new_size: Extent) -> Extent:
        """
        Mutate the requested size of the content frame.

        I cannot simply put this into the begin_page logic because I can't easily
        send a new size down to child frames in a container.
        """
        ...  # pragma: no cover

    def begin_page(self, page_number: int) -> bool:
        """Signal that the driver is starting a new page and content loading for it should be done now."""
        ...  # pragma: no cover

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the extent of all contained elements and the total extent required to draw them under the layout rules.

        Frames with flowing content should fill their entire major dimension (which is width for text) in the passed
        extent (within their padding constraints) & measure the resulting minor dimension - this extent is then is the
        minimum size to be returned.

        Frame implementors are free to pad or clip to the `requested_size` however makes sense for their framed content.

        Frame implementors are free to interpret flexible "fit to" measures in <extent> as they see fit in a way that makes
        most sense for their content. The layout manager may then call this method again with a firmer idea of maximum size
        in <extent> once it gets the result of the first measure call.

        OTOH, layout managers should have complete knowledge of space available on their page - they should prefer substituting a
        definite maximum space available to passing a "fit to" distance in <extent> where possible.

        :param extent: the maximum amount of space allocated to the frame on a single page.
        :return: the minimum amount of required for the frame

        """
        ...  # pragma: no cover

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position all visible element inside an extent.

        `do_layout` is where whitespace allocation magic should happen.

        The frame returns a Region instance that defines its local coordinate system.
        During `draw`, all positions are expressed relative this region's origin.

        The extent in the returned region contains the maximum offsets from the origin in the frame.

        There is no guarantee that the passed <target_extent> will hold all of a frame's content.
        `do_layout` implementors should fit as much as possible according to their layout rules.
        It is possible that a layout manager could call `do_layout` several times on frame
        to obtain a returned region that it likes.

        :param target_extent: the amount of space allocated to this frame's content

        :return: a region for the actual space occupied by the frame, where

            - `origin` is the offset into `target_extent` for origin in the frame's local coordinate system
            - `extent` is the offset from `origin` of the other corner of the bounding box.

        .. only:: dev_notes

            - We can actually have negative coordinates - so the returned `Region.extent` isn't a size!
              The frame is simply guaranteeing that it won't draw outsize of those bounds relative to the origin.
            - If there's negative coordinates, the frame should guarantee that it won't stray outside of the original <target_extent>.

        """
        ...  # pragma: no cover

    def draw(self, c: DisplaySurface, region: Region) -> None:
        """
        Execute drawing the visible elements inside the region on the drawing surface.

        The region passed do draw is guaranteed at least as large as the region passed to do_layout.
        draw clients should never add more content to a bigger region than has already been laid out.
        """
        ...  # pragma: no cover
