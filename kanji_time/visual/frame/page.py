# page.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model a single page in a report.

The Page class is the heart of the pagination algorithm for reports.

The pagination model works with three assumptions

1) Every ContentFrame instance manages its own content data

    - The ContentFrame can stream data through itself across multiple page or render the same data on every page
    - The draw() method of the interface updates the frame's state to indicate if

        - there's more unrendered data,
        - there's no more unrendered data but the frame can be reused to render the same data again, or
        - there's no more unrendered data and all the frame's data has been consumed.

2) Every ContentFrame has a begin_page() method

    - BeginPage signals the frame to refresh its buffers if necessary for new rendering data
    - The frame can indicate that it has nothing to do by returning False from being_page()

3) The Page itself is a ContentFrame/Container instance.

    - A report is typically managed by a controller
    - The controller implements a top-level version of begin_page() to create page layouts and populate page containers with ContentFrame
      instances as necessary.
    - For simple reports, usually only the report controller needs to implement begin_page(), but this breaks down as individual frames need
      to buffer data from some source.

- We manage physical page characteristics though a mutable global SETTINGS object that is an instance of PageSettings.
- These settings are frozen and then bound to a Page factory when we start a report - thus every new Page instance has the same physical
  properties unless the controller overrides these in the initializer call.
- The report controller typically derives from SimpleElement and implements the BeginPage method to create page layouts as needed
  from the page factory.
- Once the controller has a Page in hand, it populates it with ContentFrames and a layout strategy

.. note:: For a fixed layout, the controller only needs to create and populate one Page instance at the start of the job that it uses for
   every page.

- Because ContentFrame instances are sized dynamically to fit their content, the Page container governing the current output page must be
  measured and laid out before it is drawn.

The key feature to this model is that a report controller can make as many or as few general Page containers as it needs, varying physical
properties to fit its context.  For example,

    - the report control could have different Page layout schemes for even/odd pages for a bound book and a third layout for the first page
      of a chapter, or,
    - the first page of the report could be a content summary in portrait orientation followed by columnar output pages in landscape
      orientation of the results of an SQL query.

Class Relationships
-------------------

The overall class relationships in this model are as follows.

.. mermaid::
    :name: cd_page
    :caption: Class diagram showing high-level relationships for the Page class.

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB

        class Page
        class PageFactory
        class PageSettings
        class RenderingFrame
        class Container
        class ReportController
        note for ReportController "Implicit class - not formally defined"

        style Page fill:#aaa
        style PageFactory fill:#aaa
        style PageSettings fill:#aaa

        RenderingFrame <|-- Container

        class RenderingFrame {
            <<interface>>
            + begin_page(int page_number) bool
            + measure(extent: Extent) Extent
            + do_layout(target_extent: Extent) Region
            + draw(c: DisplaySurface, region: Region) None
            + state() States
        }

        Container <|-- Page : a page works like any other content container
        ReportController ..> RenderingFrame: implements BeginPage
        Page --* "n" RenderingFrame : children a/k/a page content
        ReportController ..* Page: populates
        PageFactory ..> Page: instantiates
        Page ..> PageFactory: provides
        PageFactory ..> PageSettings: uses


        class PageSettings {
            + create_page(**kwargs) Page
        }
        PageSettings ..> Page : creates

"""

# pylint: disable=fixme

from collections import namedtuple
from collections.abc import Mapping
import copy
from dataclasses import dataclass

from kanji_time.visual.frame.container import Container
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Region, Extent, Pos
from kanji_time.visual.layout.paper_names import PaperNames, PaperOrientations, PaperOrientation
from kanji_time.visual.protocol.content import RenderingFrame
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy


#: Physical page margins
Margins = namedtuple('Margins', "left top right bottom")

# pylint: disable=missing-class-docstring,too-few-public-methods
class Page: ...  # type: ignore

@dataclass
class PageSettings:
    """
    Model the usual suspects for page settings.

    .. mermaid::
        :name: cd_pagesettings
        :caption: Class diagram showing relationships for the PageSettings class.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB

            class Page
            class PageFactory
            class PageSettings

            style PageSettings fill:#777

            Page ..> PageFactory: provides
            PageFactory ..> Page: instantiates
            PageFactory ..> PageSettings: uses


            class PaperNames
            class Margins
            class PaperOrientation
            class PageSettings {
                + Extent page_size
                + Region printable_region
                + create_page(**kwargs) Page
            }
            PageSettings --* PaperNames : paper
            PageSettings --* Margins : margins
            PageSettings --* PaperOrientation : orientation
            PageSettings ..> Page : creates


    .. only:: dev_notes

        - PageSettings would be an ideal place to set global header/footer contents

    """
    paper: PaperNames
    margins: Margins
    orientation: PaperOrientation

    def create_page(self, **kwargs) -> Page:
        """
        Create a page container instance following the current settings.

        This method does not track the pages it creates nor modify internal state.

        :param kwargs: ad hoc extra keyword arguments to pass down to the page instance.
        :return: a new Page container instance with physical properties matching the current page settings.
        """
        return Page(self.paper, self.orientation, self.margins, **kwargs)  # type: ignore

    @property
    def page_size(self) -> Extent:
        """
        Provide the page size as an Extent instance.

        :return: the total physical page size
        """
        return Extent(*map(lambda x: Distance(x, "pt"), self.orientation(self.paper.value)))

    @property
    def printable_region(self) -> Region:
        """
        Provide the page size exclusive of margin settings.

        :return: the offset and extent into the physical page usable for content.

        Margins and printable area are illustrated below (not to scale):

        ::

            +-----------------------------------------+
            |                Top Margin               |
            |        +-----------------------+        |
            | Left   |     Printable Area    | Right  |
            | Margin |                       | Margin |
            |        +-----------------------+        |
            |               Bottom Margin             |
            +-----------------------------------------+

        """
        return Region(
            Pos(self.margins.left, self.margins.bottom),  # origin on the lower left for ReportLab
            Extent(
                self.page_size.width - (self.margins.left + self.margins.right),
                self.page_size.height - (self.margins.top + self.margins.bottom)
            )
        )


#: Global mutable default page settings
SETTINGS = PageSettings(
    PaperNames.letter,
    Margins(*map(Distance.parse, "0.5in 0.5in 0.5in 0.5in".split())),
    PaperOrientations.portrait
)


class Page(Container):  # pylint: disable=function-redefined
    """
    Represent a single page of report output.

    Instantiate a page with the physical page properties and ad hoc settings with keyword arguments.

    :param paper: name of the paper size
    :param orientation: landscape (long side at the top) or portrait (short side at the top)
    :param margins: offsets from respective edges containing the usable area
    :param kwargs: ad hoc keyword arguments to send along to the Container

    There are two key roles that Page fulfils:

        - it is the root container for all page content, and,
        - it enforces page-specific physical constraints imposed by margins and size.

    Like any other RenderingFrame instance, a Page must be measured and laid out before it can be drawn.
    However, Page delegates upwards to its parent Container to execute these tasks.

    The sequencing for generating a page of output is as follows.

    .. mermaid::
        :name: sd_single_page
        :caption: Sequence diagram for generating a page of output.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            class:
                hideEmptyMembersBox: true
        ---
        sequenceDiagram
                participant PageFactory
            participant Controller
            participant Page
            participant Frame as ContentFrame

            Controller->>PageFactory: create_page()
            PageFactory-->>Controller: Page
            Controller->>Page: add(content frames)
            Controller->>Page: measure()
            Page->>Frame: measure()
            Controller->>Page: draw()
            Page->>Frame: draw()
            Frame-->>Page: set state


    The Page class relates to other classes as below.

    .. mermaid::
        :name: cd_pagedetail
        :caption: Class diagram showing detailed relationships for the Page class.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
                class PageFactory
                note for PageFactory "A report controller owns a PageFactory instance to create Page instances from frozen page settings"
                class Page {
                    +factory() PageFactory$
                }
                class PageSettings {
                    + create_page(**kwargs) Page
                }
                class RenderingFrame
                class Container
                <<realization>>Container

                style Page fill:#777

                RenderingFrame <|-- Container

                class RenderingFrame {
                    <<interface>>
                    + begin_page(int page_number) bool
                    + measure(extent: Extent) Extent
                    + do_layout(target_extent: Extent) Region
                    + draw(c: DisplaySurface, region: Region) None
                    + state() States
                }
                note for Page "The underlying Container is populated by a report controller instance"

                Container <|-- Page : a page works like any other content container
                Page --* "n" RenderingFrame : children a/k/a page content
                PageFactory ..> Page: instantiates
                Page ..> PageFactory: provides
                PageFactory --* PageSettings: frozen copy at Factory create time


    """

    class Factory:  # pylint: disable=too-few-public-methods
        """
        Freeze the page setting for an output job and create new blank pages with these settings on demand.

        The page factory is nothing more than a callable closure around a private copy of the page settings.
        """
        def __init__(self, settings):
            self.settings = copy.copy(settings)
        def __call__(self, element_name: str, child_elements: Mapping[str, RenderingFrame], layout_strategy: LayoutStrategy, **kwargs):
            return self.settings.create_page(
                element_name=element_name,
                child_elements=child_elements,
                layout_strategy=layout_strategy,
                **kwargs
            )

    @classmethod
    def factory(cls):
        """
        Provide a factory function to create pages according to the current settings.

        Defers to the contained frozen page settings to instantiate a page.
        """
        return cls.Factory(SETTINGS)

    def __init__(self, paper: PaperNames, orientation: PaperOrientation, margins: Margins, **kwargs):
        """Initialize an empty page from physical page settings."""
        self.page_size = Extent(*map(lambda x: Distance(x, "pt"), orientation(paper.value)))
        print_area = Region(
            Pos(margins.left, margins.bottom),  # origin on the lower left for ReportLab
            Extent(
                self.page_size.width - (margins.left + margins.right),
                self.page_size.height - (margins.top + margins.bottom)
            )
        )
        super().__init__(requested_size=print_area.extent, **kwargs)
