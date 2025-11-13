# controller.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Coordinate the interaction between a page-pump loop and a report.

The :class:`PageController` protocol provides a centralized coordination scheme to allow individual rendering frame components to manage their
output data "on-demand" such that they only need to have it when their are emitting to a page that needs it. It further ensures that all
of the RenderingFrame components of a Page are positioned and ready when it it's time to draw them.

(Note, the Kanji Summary and Practice Sheet sample reports load all their data in a monolith to keep things simple - but they could do
page-by-page management during begin_page().)

Since report controller classes will typically only want to manage data, they should delegate all the page layout interactions required of a
top-level RenderFrame to their current Page instance.  The DelegatingRenderingFrame convenience class is tailor made for this purpose.

Finally, since most of the page management work of a PageController is common across all reports, the PaginatedReport convenience class can
be used as a base class to a report controller to handle these chores in a consistent fashion.

The end result of the PageController and the two convenience classes is an uncluttered interface. We've freed up ReportController classes to
focus on their job:  creating rendering frames and directing data to them on each page as needed.

.. rubric:: Class Interactions
    :heading-level: 2

The below class diagram illustrates the high level interactions of a page controller.

.. mermaid::
    :name: cd_pagecontroller
    :caption: Class relationships for the simple pagination service.

    classDiagram
        direction TB

        %% Protocols
        class RenderingFrame {
            <<interface>>
            +begin_page(page_number: int) bool
            +measure(extent: Extent) Extent
            +do_layout(target_extent: Extent) Region
            +draw(c: DisplaySurface, region: Region) None
            +state: States
        }

        class PageController {
            <<interface>>
            +begin_page(page_number: int) bool
            +layout_name(page_number: int): str
            +get_page_layout(name: str): PageLayout
            +get_page_container(name: str): Page
        }

        %% Core delegates
        class PaginatedReport {
            +begin_page(page_number: int) bool
        }

        class DelegatingRenderingFrame {
            +set_delegatee(RenderingFrame)
            +draw()
            +measure()
            +do_layout()
        }

        %% Report class
        class Report {
            +gather_report_data(glyph: str): ReportData
            +get_page_layout(layout_name): PageLayout
            +get_page_container(layout_name): Page
            +output_file: str
        }

        %% Composition/delegation structure
        PageController <|.. PaginatedReport
        RenderingFrame <|.. DelegatingRenderingFrame

        PaginatedReport <|-- Report
        DelegatingRenderingFrame <|-- Report
        Report ..> Page : delegatee

----

.. seealso:: :doc:`dev_notes/controller_notes`

----

"""

# reports/report_controller.py

from collections.abc import MutableMapping
from typing import NamedTuple, Protocol, runtime_checkable

from kanji_time.visual.frame.page import Page
from kanji_time.visual.layout.region import Extent, Region
from kanji_time.visual.protocol.content import DisplaySurface, RenderingFrame, States
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy

class DelegatingRenderingFrame(RenderingFrame):
    """
    Provide a RenderingFrame interface for a class that delegates to some other RenderFrame instance.

    :param delegatee: A RenderingFrame instance that handles all the protocol methods.
    """

    def __init__(self, delegatee: RenderingFrame | None, **kwargs):
        """
        Initialize the Delegating frame with all the data demanded by the RenderingFrame interface.

        It's unfortunate that I can't just tell the Protocol to look on my delegatee for its data.
        """
        super().__init__(**kwargs)
        if delegatee is not None:
            self.set_delegatee(delegatee)

    def set_delegatee(self, delegatee: RenderingFrame):
        """
        Assign a receiver for the delegated methods of the RenderingFrame methods.

        :param delegatee: A RenderingFrame instance (possibly new) that handles all the protocol methods.
        """
        assert delegatee is not None
        self._requested_size: Extent = delegatee._requested_size  # pylint: disable=protected-access
        self._layout_size: Extent = delegatee._layout_size  # pylint: disable=protected-access
        self._state: States = delegatee._state  # pylint: disable=protected-access
        self.content_size: Extent = delegatee.content_size
        self.delegatee: RenderingFrame = delegatee

    @property
    def state(self) -> States:
        """Produce the current state of the content frame."""
        return self.delegatee.state

    @property
    def requested_size(self) -> Extent:
        """Yield the requested space to reserve for the framed content."""
        return self.delegatee.requested_size

    @property
    def layout_size(self) -> Extent:
        """Yield the actual space (as computed during measure()) occupied by the framed content for layout."""
        return self.delegatee.layout_size

    @property
    def is_stretchy(self) -> Extent:
        """Produce true if this content can be fit to some dimensions (linearly upward only)."""
        return self.delegatee.is_stretchy

    def __bool__(self) -> bool:
        """Produce true when this rendering frame has non-trivial content."""
        return self.delegatee.__bool__()

    def resize(self, new_size: Extent) -> Extent:
        """Mutate the requested size of the content frame."""
        return self.delegatee.resize(new_size)

    def begin_page(self, page_number: int) -> bool:
        """Signal that the driver is starting a new page and content loading for it should be done now."""
        return self.delegatee.begin_page(page_number)

    def measure(self, extent: Extent) -> Extent:
        """Measure the extent of all contained elements and the total extent required to draw them under the layout rules."""
        return self.delegatee.measure(extent)

    def do_layout(self, target_extent: Extent) -> Region:
        """Position all visible element inside the region."""
        return self.delegatee.do_layout(target_extent)

    def draw(self, c: DisplaySurface, region: Region) -> None:
        """
        Execute drawing the visible elements inside the region on the drawing surface.

        The region passed do draw is guaranteed at least as large as the region passed to do_layout.
        draw clients should never add more content to a bigger region than has already been laid out.
        """
        self.delegatee.draw(c, region)


PageLayoutName = str
PageLayout = NamedTuple("PageLayout", [("child_elements", dict[str, RenderingFrame]),
                                       ("layout_strategy", LayoutStrategy)])


@runtime_checkable
class PageController(Protocol):
    """
    Behavior specification for paginating a report.

    The `PageController` protocol specifies how a paginating report driver interacts with the top-level RenderingFrame instance in a report
    to produce the correct page-breaks in the output stream.

    :param page_factory: function that produces `Page` instances on demand for each distinct page layout.
    :param page: the current `Page` instance in-process.
    :param content_size: the size of the content on <page>.
    :param _page_layout_map: the correspondence between layout names and `Page` instances holding their completed RenderingFrame layout.

    .. only:: dev_notes

        - This protocol is asking implementors for far too much data: can I do more with less?

    """

    # Review: This seems a little bossy to demand all this data
    page_factory: Page.Factory
    page: Page | None
    content_size: Extent
    _page_layout_map: MutableMapping[PageLayoutName, Page]

    def begin_page(self, page_number: int) -> bool:
        """Start a new page layout or reuse an existing one, based on data state."""
        ...

    def layout_name(self, page_number: int) -> PageLayoutName:
        """Return a layout identity string for the given page."""
        ...

    def get_page_layout(self, layout_name: PageLayoutName) -> PageLayout:
        """Return per-page frame content."""
        ...

    def get_page_container(self, layout_name: PageLayoutName) -> Page:
        """
        Return a new Page instance for the given layout identity.
        """
        ...


class PaginatedReport(PageController):
    """
    Provide concrete pagination services for KanjiTime reports.

        - Supports persistent layout templates (Pages) selected by page type.
        - Delegates per-page content updates to get_frame_updates().
        - Pages are lazily created on first request using create_page_layout().

    Provides:
        - Common `begin_page()` logic

    Subclass may implement:
        - get_page_type(page_number) -> str
        - get_frame_updates(page_number) -> dict[str, RenderingFrame | None]
        - create_page_layout(page_type, page_number) -> Page

    The protocol requires definitions in this class for
        - self.page_factory
        - self.page
        - self._pages

    .. only:: dev_notes

        - I could pass layouts as dict-valued kwargs.  Maybe?  Think on it.

    """
    def __init__(self, **kwargs):
        """Initialize an instance with data symbols required by the ReportController protocol."""
        super().__init__(**kwargs)
        self.page_factory = Page.factory()
        self.page: Page | None = None
        self.content_size = Extent.zero
        self._page_layout_map: MutableMapping[str, Page] = {}
        # I could pass layouts as dict-valued kwargs.  Maybe?  Think on it.
        self.default_layout = kwargs["default_layout"] if "default_layout" in kwargs else (None, None)

    def begin_page(self, page_number: int) -> bool:
        """
        Start processing output for a new page.

        Each page number is associated with a layout name, which in turn corresponds to a page container.

            - We create page containers lazily on-demand as we see each new layout name.
            - This stub implementation of PageController assigns the layout name "default_layout" to every page.
              Subclasses override `layout_name()` for more complex structuring.

        :param page_number: the sequence number of the page in this report.
            This sequence number will not correspond the output page number when an aggregator composes multiple reports into a larger whole.

        .. only:: dev_notes

            - New page condition is hokey: state flags overlap with the begin_page return value.  Can I clean this up?
            - BIG: we're only asking the current layout if there's more data with page.begin_page -- other's may have data too.
            - Should the measure and layout calls stay here or be factored out? or pushed into Page.begin_page()?

        """
        # Review this condition for starting a new page
        if self.page is not None and States.have_more_data not in self.page.state:
            return False

        # Map a layout to a page container, creating the container new layouts on-demand
        layout_name = self.layout_name(page_number)
        if layout_name not in self._page_layout_map:
            new_page = self.get_page_container(layout_name)
            self._page_layout_map[layout_name] = new_page
        self.page = self._page_layout_map[layout_name]

        # Let the page container pass the begin page message down to its children if it wants.
        # It will come back with True if there's anything to do for this page.
        #
        # BIG ISSUE - is it possible that other page layouts have more data?
        assert self.page is not None
        if not self.page.begin_page(page_number):
            return False

        # Do the layout chores
        # Should the measure and layout calls stay here or be factored out? or pushed into Page.begin_page()?
        region = self.page_factory.settings.printable_region
        self.page.measure(region.extent)
        self.page.do_layout(region.extent)
        return True

    def layout_name(self, page_number: int) -> str:
        """Return a layout identity string for the given page."""
        return "default_layout"

    def get_page_layout(self, layout_name: PageLayoutName) -> PageLayout:
        """Return per-page type content frames."""
        if layout_name != "default_layout" or self.default_layout is None:
            raise NotImplementedError(f"No page layout implemented for the layout name '{layout_name}'.")
        return self.default_layout

    def get_page_container(self, layout_name: PageLayoutName) -> Page:
        """
        Return a new Page instance for the given layout identity.

        The default stub simply return vertically stacked page of rendering frames.
        """
        child_elements, layout_strategy = self.get_page_layout(layout_name)
        return self.page_factory(
            f"{self.__class__.__name__} layout '{layout_name}'",
            child_elements,
            layout_strategy
        )
