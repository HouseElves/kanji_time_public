# report.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
.. rubric:: Kanji Practice Sheet
    :heading-level: 2

Create a stroke order diagram and practice grids for a particular kanji or kana.

This report is close to the vision for how to describe reports in general.

.. mermaid::
    :name: cd_practicesheet
    :caption: Class relationships for the kanji practice sheet.

    ---
    config:
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TB
            class RenderingFrame
            class SimpleElement
            class Container
            class Page
            class PracticeSheet
            class PracticeSheetData

            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            <<realization>> Container
            <<realization>> PracticeSheet

            RenderingFrame <|-- SimpleElement
            RenderingFrame <|-- Container
            Container <-- Page

            SimpleElement <|-- PracticeSheet
            Page <.. PracticeSheet : impersonates RenderingFrame

            PracticeSheet --o PracticeSheetData : report_data

.. only:: dev_notes

    - Review the adapter nomenclature conventions: adapter.SVGtoRL.Drawing, RLtoSVG.Drawing ?

"""
# pylint: disable=fixme

import os
from typing import cast

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

import kanji_time.settings as settings
# Review the adapter nomenclature conventions: adapter.SVGtoRL.Drawing, RLtoSVG.Drawing ?
from kanji_time.reports.practice_sheet.document import PracticeSheetData
from kanji_time.reports.controller import PageLayout, PageLayoutName, PaginatedReport, DelegatingRenderingFrame
from kanji_time.visual.frame.drawing import ReportLabDrawing
from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.frame.page import Page
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent
from kanji_time.visual.layout.stack_layout import StackLayoutStrategy
from kanji_time.visual.protocol.content import DisplaySurface

from kanji_time.utilities.xml import in_typeface
from kanji_time.utilities.general import log, pdf_canvas

# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


# kanji_list = '鷄合晴格好悪上五以'  # しの何分初別功単原台君味嘘図圖土地子密屹度心愛成戸所教文斤書有横無珍現生産由発知禽私秘紋紙緒考者自至表言語諺識近邪音馬魔鳥鶏鷄鹿':


class Report(PaginatedReport, DelegatingRenderingFrame):
    """
    Define a report containing a kanji stroke diagram and practice areas for brushing it.

    :param report_data: the supporting data document necessary to generate the report content.

    .. mermaid::
        :name: cd_practicesheet_detail
        :caption: Class relationship details for the kanji practice sheet.

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
            class PracticeSheet

            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            <<realization>> Container
            <<realization>> PracticeSheet

            RenderingFrame <|-- SimpleElement
            RenderingFrame <|-- Container
            Container <-- Page

            class Page {
                +factory()$
            }
            Page : Extent page_size
            Page : Region print_area

            class PracticeSheet
            SimpleElement <|-- PracticeSheet
            Page <.. PracticeSheet : impersonates RenderingFrame

            class PracticeSheet {
                +begin_page(self, int page_number) bool
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }
            PracticeSheet : Extent content_size
            PracticeSheet : States state
            PracticeSheet : tuple~float~ paper_size
            PracticeSheet --o PracticeSheetData : report_data
            PracticeSheet --* ReportLabDrawing : stroke_diagram
            PracticeSheet --* "4" ReportLabDrawing : practice_strip
            PracticeSheet --* "2" FormattedText : practice_heading, stroke_heading
            PracticeSheet --* Page-Factory : make_page_layout
            PracticeSheet --o Page : page_layout

    """

    Data = PracticeSheetData
    @classmethod
    def gather_report_data(cls, glyph: str, **kwargs) -> PracticeSheetData:  # pylint: disable=unused-argument
        """
        Fetch data required for the PracticeSheet report.

        :param glyph: the kanji glyph for which we want a practice sheet
        :param kwargs: ad hoc keyword arguments.

        :return: a dataset reference ready to pass to the PracticeSheet initializer.
        """
        return PracticeSheetData(glyph)

    CELL_SIZE = Distance.parse("1in")

    def __init__(self, report_data: PracticeSheetData):
        """
        Initialize the POC report as a strip with three elements:  text at the bottom, a rule, then the banner.

        .. only:: dev_notes

            - what are all the failure modes in the math and allocating resources?
            - there is no edge case handling!
            - the hardcoded distances between the page elements should either be sent in as config params or computed by a whitespace strategy

        """
        super().__init__(delegatee=None)

        page_size = self.page_factory.settings.printable_region.extent
        self.report_data = report_data
        steps = len(report_data.glyph_svg.strokes) + 1

        normal_style = getSampleStyleSheet()['Normal']

        # Review: what are all the failure modes?  I have no edge case handling!
        max_columns = (page_size.width // self.CELL_SIZE)  # + int((page_size.width % self.CELL_SIZE) > 0)
        step_columns = steps if (steps*self.CELL_SIZE <= page_size.width) else max_columns
        stroke_heading = Paragraph(in_typeface('Helvetica', "Stroke Order Diagram"), style=normal_style)
        stroke_diagram = report_data.stroke_diagram(step_columns, Extent(self.CELL_SIZE, self.CELL_SIZE))
        practice_heading = Paragraph(in_typeface('Helvetica', "Practice Grids"), style=normal_style)
        practice_strip = report_data.practice_strip(max_columns, Extent(self.CELL_SIZE, self.CELL_SIZE))

        self.common_elements = {
            #  this spacer shouldn't be necessary:  my north anchoring on the stroke diagram isn't doing anything for me
            # "empty": EmptySpace(Extent(page_size.width, page_size.height - Distance(stroke_diagram.width, "pt"))),
            #  *configurable ?*  Should these hardcoded distances be configuration parameters?
            "practice_strip 1": ReportLabDrawing(
                Extent(page_size.width, Distance.fit_to),
                AnchorPoint.NW,
                practice_strip
            ),
            "practice_strip 2": ReportLabDrawing(
                Extent(page_size.width, self.CELL_SIZE + Distance(0.25, "in")),
                AnchorPoint.NW,
                practice_strip
            ),
            "practice_strip 3": ReportLabDrawing(
                Extent(page_size.width, self.CELL_SIZE + Distance(0.25, "in")),
                AnchorPoint.NW,
                practice_strip
            ),
            "practice_strip 4": ReportLabDrawing(
                Extent(page_size.width, self.CELL_SIZE + Distance(0.25, "in")),
                AnchorPoint.NW,
                practice_strip
            ),
            "practice heading": FormattedText(
                Extent(page_size.width, Distance(normal_style.leading, "pt")),
                AnchorPoint.W,
                [practice_heading],
                do_not_consume=True
            ),
            "stroke_diagram": ReportLabDrawing(
                Extent(page_size.width, Distance(stroke_diagram.height, "pt") + Distance(0.25, "in")), # 0.25" margin above
                AnchorPoint.NW,
                stroke_diagram
            ),
            "stroke heading": FormattedText(
                Extent(page_size.width, Distance(normal_style.leading, "pt")),
                AnchorPoint.W,
                [stroke_heading],
                do_not_consume=True
            )
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
        return f"{self.report_data.glyph}_practice.pdf"

    @property
    def paper_size(self) -> tuple[float, float]:
        """
        Produce the paper size as a ReportLab native tuple.

        :return: paper size in points as a (width, height) tuple of floats.
        """
        page_size = self.page_factory.settings.page_size
        return page_size.width.pt, page_size.height.pt

    def layout_name(self, page_number: int) -> PageLayoutName:
        """
        Produce the layout identity for a given page number.

        The practice sheet always returns "practice_sheet".

        :param page_number: ignored.
        :return: the string "practice_sheet".
        """
        return "practice_sheet"

    def get_page_layout(self, layout_name: PageLayoutName) -> PageLayout:
        """
        Produce the rendering frames and layout strategy for <layout_name>.

        The practice sheet only has one layout described in <self.common_elements> that we layout out as a vertical stack.

        :param layout_name:  Should always be "practice_sheet"
        :return: the common elements dictionary of rendering frames defined during init.

        .. only:: dev_notes

            - Consider failure modes.  What if the common elements don't exist?

        """
        assert layout_name == "practice_sheet", f"Unexpected layout passed to {self.__class__.__name__}.get_page_layout()."
        return PageLayout(self.common_elements, StackLayoutStrategy("vertical"))

    def get_page_container(self, layout_name: PageLayoutName) -> Page:
        """Intercept creating a page layout container to set the RenderingFrame delegatee."""
        page = super().get_page_container(layout_name)
        self.set_delegatee(page)
        return page
