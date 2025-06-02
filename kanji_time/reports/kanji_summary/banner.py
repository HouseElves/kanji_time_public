"""Define a custom frame for the Kanji Summary banner."""

from kanji_time.reports.kanji_summary.document import KanjiReportData
from kanji_time.reports.kanji_summary.kanji_summary import KanjiSummary
from kanji_time.reports.kanji_summary.radical_summary import RadicalSummary

from kanji_time.visual.frame.container import Container
from kanji_time.visual.frame.drawing import ReportLabDrawing
from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent
from kanji_time.visual.layout.stack_layout import StackLayoutStrategy
from kanji_time.visual.protocol.content import RenderingFrame


class SummaryBanner(Container):
    """
    Represent the top banner section of the Kanji information sheet on the first page of output.

    The banner has three sections:

        * The left section contains an image of the kanji
        * The middle section contains a terse definition and other information for the kanji
        * The right section describes the traditional radical for the kanji

    Each section is in its own rendering frame instance.  Specialized rendering frames for the middle and right
    sections are defined in :py:class:`KanjiSummary` and :py:func:`RadicalSummary`, respectively.

    The Summary Banner is just a frame container -- all the logic is the base class.
    Our only job here it to pass down the contained frames and their content.

    :param size: - the total requested size to reserve for this element and all of its child elements, if possible.
    :param report_data: The "document" for this "view" element that contains source data for its rendering frames.

    .. mermaid::
        :name: cd_infosheet_banner1
        :caption: Class relationships for the kanji information report 1st page banner.

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
            class Container

            <<interface>> RenderingFrame
            <<realization>> Container
            RenderingFrame <|-- Container
            Container <|-- SummaryBanner

            Container --o StackLayoutStrategy : layout_strategy
            Container --* Extent : content_size

            SummaryBanner --* ReportLabDrawing : kanji_drawing
            SummaryBanner --* KanjiSummary : summary_definition
            SummaryBanner --* RadicalSummary : radical

    """

    def __init__(self, size: Extent, report_data: KanjiReportData):
        """Initialize the banner as a strip with 3 regions:  an drawing, text, and mixed drawing/text."""
        elements: dict[str, RenderingFrame] = {
            "svg": ReportLabDrawing(Extent(size.height, size.height), AnchorPoint.CENTER, report_data.banner_kanji),
            "middle": KanjiSummary(Extent(Distance.parse("*"), size.height), report_data.text["banner"]),
            "right": RadicalSummary(Extent(RadicalSummary.TEXT_AREA_WIDTH, size.height), report_data),
        }
        super().__init__("banner frame", size, elements, StackLayoutStrategy("horizontal"))


class SummaryBannerPage2On(Container):
    """
    Represent the top banner section of the Kanji information sheet on the second and subsequent pages of output.

    For page 2 onwards, we shrink the banner down to a minimum:  a smaller version of the drawn kanji, the terse definition and a
    "continued" indicator.

    :param size: - the total requested size to reserve for this element and all of its child elements, if possible.
    :param report_data: The "document" for this "view" element that contains source data for its rendering frames.

    .. mermaid::
        :name: cd_infosheet_banner2
        :caption: Class relationships for the kanji information report 2nd page onwards banner.

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
            class Container

            <<interface>> RenderingFrame
            <<realization>> Container
            RenderingFrame <|-- Container
            Container <|-- SummaryBannerPage2On

            Container --o StackLayoutStrategy : layout_strategy
            Container --* Extent : content_size

            SummaryBannerPg2On --* ReportLabDrawing : small_kanji_drawing
            SummaryBannerPg2On --* FormattedText : continued

    """

    def __init__(self, size, report_data: KanjiReportData):
        """Initialize the banner as a strip with 3 regions:  an drawing, text, and mixed drawing/text."""
        elements: dict[str, RenderingFrame] = {
            "small_svg": ReportLabDrawing(
                Extent(size.height, size.height),
                AnchorPoint.CENTER,
                report_data.get_reportlab_glyph(Extent(size.height, size.height))
            ),
            "continued": FormattedText(
                Extent(Distance.fit_to, size.height),
                AnchorPoint.CENTER,
                report_data.text["page2on"],
                do_not_consume=True
            ),
        }
        super().__init__("small banner", size, elements, StackLayoutStrategy("horizontal"))
