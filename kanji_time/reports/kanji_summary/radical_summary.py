"""Define a custom frame for the radical portion of the Kanji Summary banner."""

from kanji_time.reports.kanji_summary.document import KanjiReportData
from kanji_time.visual.frame.drawing import ReportLabDrawing
from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.frame.simple_element import SimpleElement
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent, Pos, Region
from kanji_time.visual.protocol.content import DisplaySurface, RenderingFrame, States


class RadicalSummary(SimpleElement):
    """
    Represents the contents of the right side of the kanji information sheet banner.

        * This pane has a smaller version of the kanji SVG containing only the strokes in the traditional radical.
        * There is right justified information text about the radical underneath the image such as its name and meanings.

    The smaller SVG is half the height of this element.

    :param requested_size:  The total layout extent to reserve for this element, if possible.
    :param report_data: The "document" for this "view" element that contains source data for its rendering frames.

    .. mermaid::
        :name: cd_infosheet_radical
        :caption: Class relationships for the kanji information report radical.

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
            class RadicalSummary {
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }
            RenderingFrame <|-- SimpleElement
            SimpleElement <|-- RadicalSummary
            RadicalSummary --* Extent : content_size
            RadicalSummary --* Sequence : regions
            RadicalSummary --* ReportLabDrawing : radical_drawing
            RadicalSummary --* FormattedText : radical_description
            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            <<realization>> RadicalSummary

    .. only:: dev_notes

        - Represent this as as a vanilla horizontally stretchy vertical stack with a minimum size to fit the SVG.
          I don't need to have a customized layout.

    """

    TEXT_AREA_WIDTH = Distance.parse("2in")

    def __init__(self, requested_size: Extent, report_data: KanjiReportData):
        """Initialize the Radical Summary element with its layout size and source data."""
        super().__init__(requested_size)

        self.content_size = Extent(Distance.zero, Distance.zero)
        half_height = requested_size.height // 2
        self.radical: dict[str, RenderingFrame] = {
            "drawing": ReportLabDrawing(Extent(half_height, half_height), AnchorPoint.CENTER, report_data.radical_kanji),
            "explanation": FormattedText(Extent(requested_size.width, half_height), AnchorPoint.NE, report_data.text["radical"]),
        }
        self.regions: dict[str, Region] = {}
        self.drawing_extent = Extent.zero
        self.text_extent = Extent.zero

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the minimum size around all the content in the Radical Summary element.

        We need room for the radical drawing and the explanatory text below it.

        :param extent: The estimated size for this element in the final layout - used by text elements to compute height after line breaks.

        :return: min_size - the least amount of space that can be occupied by the content ignoring whitespace requests.
        """
        self._state = States.needs_layout
        if not self.requested_size:
            return Extent(Distance.fit_to, Distance.fit_to)

        self.drawing_extent = self.radical["drawing"].measure(extent)
        self.text_extent = self.radical["explanation"].measure(self.radical["explanation"].requested_size & extent)
        self.content_size = Extent(
            max(self.drawing_extent.width, self.text_extent.width, self.requested_size.width),
            self.drawing_extent.height + self.text_extent.height
        )
        return self.content_size

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Reserve layout space for the radical's SVG drawing and for its explanation text.

        The reserved space includes all the requested whitespace surrounding the content implicit in its
        requested size given at its initialization.

        :param target_extent: the size of the space allocated to this element in the layout.

        :return: region - a private coordinate space for correctly positioning this element in the target extent.
        """
        self._state = States.ready

        self.regions = {
            "drawing": Region(
                Pos(target_extent.width - self.drawing_extent.width, target_extent.height - self.drawing_extent.height),
                self.drawing_extent
                ),
            "explanation": Region(
                Pos(Distance.zero, Distance.zero),
                Extent(target_extent.width, target_extent.height - self.drawing_extent.height)
            )
        }
        return Region(
            Pos(target_extent.width - self.content_size.width, Distance.zero),
            self.content_size
        )

    def draw(self, c: DisplaySurface, region: Region):
        """
        Render the Radical Summary's SVG drawing and explanation text in the passed coordinate space.

        :param c: a surface that knows how to execute the drawing commands that we send to it.
        :param region: a coordinate space for drawing independent of surrounding elements.
        """
        self._state = States.drawn | States.reusable

        origin = region.origin
        for name, element in self.radical.items():
            element.draw(c, self.regions[name] + origin)
