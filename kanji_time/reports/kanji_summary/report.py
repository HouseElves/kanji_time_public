"""
Create a summary information sheet for a kanji.

The intent of a Kanji Summary is to give context for a kanji when practicing its strokes on a practice sheet.

The Kanji Summary contains

    - a banner with an image of the kanji, its name, a short definition, its readings, and its traditional radical, and,
    - a body containing different interpretations and specific readings for the kanji.

Some of these summaries can be quite short at half a page or so.  Some can span several pages with multiple glosses for the kanji.
On pages after the first, we abbreviate the banner to a smaller kanji image with the text "continued".

The banners themselves are implemented in this package in the module banner.py.

All the different portions of the report that render content are implemented in their own RenderingFrame instances.
The Kanji Summary and Radical Summary portions on the first page banner are implemented as custom RenderingFrame instances in their own modules
in this package, namely kanji_summary.py and radical_summary.py.

The rest of the report content uses predefined rendering frames for text and drawings defined in the visual.frames package.

The heart the reporting algorithm is that we minimize duplicated work for mundane chores of layout.
A given report doesn't really have much to do beyond defining frames for content and hooking up the data.
The report itself uses one or more visual.frames.Container instances to hold the content and defers to a LayoutStrategy instance to present it.

Class Relationships
-------------------

The Kanji Information Sheet interacts with other classes as below.

.. mermaid::
    :name: cd_infosheet
    :caption: Class relationships for the kanji information report.

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB
            class Page
            class Page-Factory

            class KanjiReport
            class RadicalSummary
            class KanjiSummary
            class SummaryBanner
            class SummaryBannerPg2On

            class RenderingFrame
            class SimpleElement
            class Container

            RenderingFrame <|-- Container
            Container <|-- SummaryBanner
            Container <|-- SummaryBannerPg2On

            RenderingFrame <|-- SimpleElement
            SimpleElement <|-- KanjiSummary
            SimpleElement <|-- RadicalSummary
            SimpleElement <|-- KanjiReport

            <<interface>>RenderingFrame
            <<abstract>>SimpleElement
            <<realization>>Container
            <<realization>>KanjiSummary
            <<realization>>RadicalSummary
            <<realization>>KanjiReport

            class RenderingFrame {
                <<interface>>
                + begin_page(int page_number) bool
                + measure(extent: Extent) Extent
                + do_layout(target_extent: Extent) Region
                + draw(c: DisplaySurface, region: Region) None
                + state() States
            }

            class RadicalSummary {
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }

            class KanjiSummary {
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }

            class KanjiReport {
                - _get_banner(self, int page_number) RenderingFrame
                +begin_page(self, int page_number) bool
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }
            KanjiReport --* KanjiReportData : report_data
            KanjiReport --* Page-Factory : new_page
            KanjiReport --* Page : page_layout
            Container <|-- Page

----

"""
# pylint: disable=fixme

import os
from typing import cast
from fractions import Fraction
import logging
import copy

# ReportLab PDF generator
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors
from reportlab import rl_config

# KanjiTime Imports
import kanji_time.settings as settings
from kanji_time.utilities.general import log, pdf_canvas

from kanji_time.reports.controller import DelegatingRenderingFrame, PageLayout, PageLayoutName, PaginatedReport
from kanji_time.reports.kanji_summary.banner import SummaryBanner, SummaryBannerPage2On
from kanji_time.reports.kanji_summary.document import KanjiReportData, build_data_object

from kanji_time.visual.protocol.content import DisplaySurface, States
from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.frame.page import Page
from kanji_time.visual.frame.page_rule import HorizontalRule
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent
from kanji_time.visual.layout.stack_layout import StackLayoutStrategy


# Configuring imports
rl_config.allowTableBoundsErrors = True
logger = logging.getLogger(__name__)


class Report(PaginatedReport, DelegatingRenderingFrame):
    """
    Define a detailed dictionary lookup report for a particular kanji.

    This class started life as a proof-of-concept to exercise all the reportlab and svgwrite features that I would need for Kanji Time
    during development.

    It has evolved into this `Report` class that binds the dictionary data to their associated rendering frames.
    The pagination and driving logic for the report has been factored out to general-purpose data types for those roles.

    A :python:`kanji_summary.Report` instance

        - uses the `PaginatedReport` mix-in as controller for producing pages,
        - behaves as a SimpleElement instance that wraps around a Page container the `DelegatingRenderingFrame` base,
        - provides data independently of UX objects via :python:`kanji_summary.Report.gather_report_data`, and,
        - provides distinct layout templates and rendering frame UX objects via `PaginatedReport` method overrides.

    Initialize a KanjiReport with the following:

    :param size: - the total requested size to reserve for this element and all of its child elements, if possible.
    :param report_data: The "document" for this "view" element that contains source data for its rendering frames.

    Class Interactions
    ------------------

    The KanjiReport uses the BeginPage method to produce and abbreviated version of the banner on the 2nd and subsequent pages.
    This diagram shows the players in this interaction.

    .. mermaid::
        :name: sd_infosheet_dynamic_layout
        :caption: Sequence diagram for changing the page layout in the Kanji Information report

        sequenceDiagram
            participant R as KanjiReport
            participant B1 as SummaryBanner
            participant B2 as SummaryBannerPg2On

            R->>R: begin_page(page_number)
            alt page_number == 1
                R->>B1: instantiate()
            else page_number ≥ 2
                R->>B2: instantiate()
            end

    More detailed class relationships are as below.

    .. mermaid::
        :name: cd_infosheet_detail
        :caption: Class relationship details for the kanji information report.

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
            class Container
            class KanjiReport

            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            <<realization>> Container
            <<realization>> KanjiReport

            RenderingFrame <|-- SimpleElement
            RenderingFrame <|-- Container
            Container <-- Page

            class Page {
                +factory()$
            }
            Page : Extent page_size
            Page : Region print_area

            class KanjiReport
            SimpleElement <|-- KanjiReport
            Page <.. KanjiReport : impersonates RenderingFrame interface for

            class KanjiReport {
                - _get_banner(self, int page_number) RenderingFrame
                +begin_page(self, int page_number) bool
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }
            KanjiReport : Extent content_size
            KanjiReport --* HorizontalRule : rule
            KanjiReport --* FormattedText : dictionary_entries
            KanjiReport --o KanjiReportData : report_data
            KanjiReport --* Page-Factory : make_page_layout
            KanjiReport --o Page : page_layout

    .. only:: dev_notes

        - Review: is the `sd_infosheet_dynamic_layout` Mermaid diagram in the wrong spot?  Generalize it and put that with `PaginatedReport`?

    """

    Data = KanjiReportData
    @classmethod
    def gather_report_data(cls, glyph: str, **kwargs) -> KanjiReportData:
        """
        Fetch data required for the Kanji Information report.

        :param glyph: the kanji glyph for which we want a practice sheet
        :param kanji_drawing_width (optional Distance keyword): width of the large kanji banner drawing.
        :param kanji_drawing_height (optional Distance keyword): height of the large kanji banner drawing.
        :param kwargs: ad hoc extra keyword arguments.

        :return: a dataset reference ready to pass to the KanjiReport initializer.
        """
        kanji_drawing_width = min(kwargs.get("kanji_drawing_width", cls.KANJI_DRAWING_SIZE), cls.KANJI_DRAWING_SIZE)
        kanji_drawing_height = min(kwargs.get("kanji_drawing_height", cls.KANJI_DRAWING_SIZE), cls.KANJI_DRAWING_SIZE)
        return build_data_object(glyph, Extent(kanji_drawing_width, kanji_drawing_height))

    BANNER_HEIGHT = Distance.parse("2in")
    KANJI_DRAWING_SIZE = BANNER_HEIGHT
    RULE_THICKNESS = Distance(Fraction(1, 64), "in")
    RULE_COLOR = colors.black

    def __init__(self, report_data: KanjiReportData):
        """Initialize the POC report as a strip with three elements:  text at the bottom, a rule, then the banner."""
        super().__init__(delegatee=None)
        self.report_data = report_data
        page_size = self.page_factory.settings.printable_region.extent
        self.common_elements = {
            "content": FormattedText(Extent(page_size.width, Distance.fit_to), AnchorPoint.NW, self.report_data.text["body"]),
            "hrule": HorizontalRule(Extent(page_size.width, self.RULE_THICKNESS), self.RULE_COLOR),
        }

    @property
    def output_file(self) -> str:
        """
        Produce the default file name for the report output.

        We guarantee that different glyphs produce different file names.
        But, we do not guarantee uniqueness through time.
        The same file name may be produced in the future for the same glyph.

        :return: a file name unique to this run and to the reported glyph.
        """
        return f"{self.report_data.radical_num}_{self.report_data.glyph}_summary.pdf"


    def layout_name(self, page_number: int) -> PageLayoutName:
        """
        Produce the layout identity for a given page number.

        The practice sheet always returns "practice_sheet".

        :param page_number: ignored.
        :return: the string "practice_sheet".
        """
        if page_number == 1:
            return "first page"
        return "subsequent pages"

    def _get_banner(self, layout_name: PageLayoutName):
        """
        Create a banner section:  page 1 is larger with more information; page 2 onwards is smaller.

        :param layout_name:  Should always be "first page" or "subsequent pages".
        :return: A rendering frame containing the page banner.
        :raises: ValueError if we don't recognize the layout_name.
        """
        page_size = self.page_factory.settings.printable_region.extent
        if layout_name == "first page":
            return SummaryBanner(Extent(page_size.width, self.BANNER_HEIGHT), self.report_data)
        if layout_name == "subsequent pages":
            return SummaryBannerPage2On(Extent(page_size.width, self.BANNER_HEIGHT//2),self.report_data)
        raise ValueError(f"Unexpected page layout '{layout_name}' in KanjiReport._get_banner()")

    def get_page_layout(self, layout_name: PageLayoutName) -> PageLayout:
        """
        Produce the rendering frames and layout strategy for <layout_name>.

        The Kanji Summary has a smaller banner footprint after page 1.
        We'll reuse the same frames for the rest of the content.

        :param layout_name:  Should always be "first page" or "subsequent pages".
        :return: the common elements dictionary of rendering frames defined during init + a context appropriate banner instance.
        :raises: ValueError if we don't recognize the layout_name - passed up from _get_banner().

        .. only:: dev_notes

            - What about failure modes?  What if the common elements don't exist?

        """
        banner = self._get_banner(layout_name)
        children = copy.copy(self.common_elements)
        children["banner"] = banner
        return PageLayout(children, StackLayoutStrategy("vertical"))

    def get_page_container(self, layout_name: PageLayoutName) -> Page:
        """Intercept creating a page layout container to set the RenderingFrame delegatee."""
        page = super().get_page_container(layout_name)
        self.set_delegatee(page)
        return page


def generate(kanji_list: str):
    """
    Produce a complete Kanji summary report.

    This function started out life as a main report execution function.
    It's now strictly a debug-entry point to the Kanji Summary report - the original report execution logic from here has been factored
    out to a general purpose report driver.

    :param kanji_list: a list of Unicode glyphs for which to generate a kanji information sheet.

    The core pagination logic is as follows.

    .. mermaid::
        :name: fc_infosheet_generate
        :caption: Pagination process flowchart.

        flowchart TD
            start([Start Summary Generation])
            initPS[Initialize PageSettings]
            buildKD[Build KanjiReportData]
            initReport[Initialize KanjiReport]
            pageLoop{More Data Available?}
            beginPage[Begin New Page Layout]
            drawReport[Draw Kanji Report Page]
            endSummary([Summary Generation Complete])

            start --> initPS
            initPS --> buildKD
            buildKD --> initReport
            initReport --> pageLoop
            pageLoop -->|Yes| beginPage
            beginPage --> drawReport
            drawReport --> pageLoop
            pageLoop -->|No| endSummary

    .. only:: dev_notes

        - the above `fc_infosheet_generate` flowchart is also relevant to `PaginatedReport` - move (copy?) it.
        - failure modes again:  what if I don't have any useful information for the passed kanji?
        - need a backing data store for kana, not just for kanji
        - would be nice to process multiple kanji in one report with practice sheets interleaved

    """
    with log("./kanji.log", logging.INFO):

        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

        # I need a database for kana - borrow heavily from Wiktionary -- see experiments.ipynb for REST queries
        # Nice to have: one report with multiple kanji -> info interleaved with the stroke diagram

        for glyph in kanji_list:
            print(f"Processing {glyph}...", end="")
            page_number: int = 1
            kanji_data = build_data_object(glyph, Extent(Distance.parse("2in"), Distance.parse("2in")))
            logging.info("Processing %s", glyph)
            kanji_summary_page = Report(kanji_data)
            page_settings = kanji_summary_page.page_factory.settings
            page_size = tuple(map(lambda x: x.pt, page_settings.page_size))
            file_name = f"{kanji_data.radical_num}_{glyph}_summary.pdf"
            with pdf_canvas(os.path.join(settings.report_directory, file_name), pagesize=page_size) as pdf:
                # kanji_summary_page.measure(page_settings.printable_region.extent)
                # kanji_summary_page.do_layout(page_settings.region.extent)
                while kanji_summary_page.begin_page(page_number):
                    print(f"{page_number}...", end="")
                    kanji_summary_page.draw(cast(DisplaySurface, pdf), page_settings.printable_region)
                    pdf.showPage()
                    if States.have_more_data not in kanji_summary_page.state:
                        break
                    page_number += 1
            print("done")
