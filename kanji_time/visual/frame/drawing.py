# drawing.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Define a layout container for ReportLab format scalable vector drawings.


.. only:: dev_notes

    - this should be a generic SVG container with a ReportLab adapter.
      I.e. decouple the ReportLab implementation from the SVG vector graphics in :python:`visual.frame.drawing.Drawing`.

    .. seealso:: :doc:`dev_notes/drawing_notes`

----

"""

# pylint: disable=fixme

from fractions import Fraction

from reportlab.graphics import renderPDF
from reportlab import rl_config

from kanji_time.visual.protocol.content import DisplaySurface, States
rl_config.allowTableBoundsErrors = True

# pylint: disable=wrong-import-position, wrong-import-order
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.region import Region, Extent, Pos
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.frame.simple_element import SimpleElement
from kanji_time.adapter.svg import RLDrawing

# pylint: disable=wrong-import-position, wrong-import-order
import logging
logger = logging.getLogger(__name__)


class ReportLabDrawing(SimpleElement):
    """
    Represent a rendering frame containing a ReportLab formatted vector drawing.

    - move away from ReportLab and tuck that technology-specific logic into an adapter
      I just want a -- drawing -- here, which will for all intents and purposes make this class
      just a hollow datatype name that has related technology specialization via aggregation or adapters.

    Initialize with

    :param requested_size: the preferred amount of space to reserve for the frame content
    :param anchor: the rough location in the owning frame
    :param drawing: vector graphic drawing ready to render on a ReportLab surface.

    A ReportLabDrawing instance has the same general class relationships as any other SimpleElement:
    it is responsible for its own measurement, layout, and drawing and owns its own specialized content
    for the rendering technology. In this case, the content is a ReportLab Graphics Drawing instance.

    .. mermaid::
        :name: cd_drawing
        :caption: Class relationships for an vector graphics drawing frame.

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
            SimpleElement <|-- ReportLabDrawing

            class ReportLabDrawing {
                <<<realization>>>
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }

            ReportLabDrawing --o RLDrawing : drawing
    """

    def __init__(self, requested_size: Extent, anchor: AnchorPoint, drawing: RLDrawing):
        """
        Initialize the content with a ReportLab scalable vector drawing.

        .. only:: dev_notes

            - zero valued defaults are ugly - see how a Maybe type works here.

        """
        assert requested_size is not None
        super().__init__(requested_size)
        self.anchor = anchor
        self.drawing = drawing
        self.drawing_origin = Pos.zero
        self.content_size = Extent.zero  # should be None.  Really, "maybe" - can I make Maybe a class level mixin verb?
        # self.drawing.renderScale = 0.5

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the minimum size of the element.

        :param extent: the estimated space allocated to the drawing in the final layout.

        :return: the amount of space required for the drawing.

        .. only:: dev_notes

            - Do I really need to measure a drawing when I can scale vector graphics on demand?
              I'd say yes since I still need to respect requested sizes and anchor point positioning.

        """
        self._state = States.needs_layout

        if not extent:
            extent = Extent.zero
        assert self.requested_size is not None
        minimum_size = self.requested_size  # | extent  # | => Extent union operator
        if not self.drawing:
            return minimum_size

        x1, y1, x2, y2 = b if (b := self.drawing.getBounds()) is not None else (0.0, 0.0, 0.0, 0.0)
        self.content_size = Extent(
            Distance(Fraction(abs(x2 - x1)), "pt", at_least=True),  # type: ignore
            Distance(Fraction(abs(y2 - y1)), "pt", at_least=True)  # type: ignore
        )
        self.drawing_origin = Pos(Distance(x1, "pt"), Distance(y1, "pt"))

        return minimum_size | self.content_size

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position the drawing in its allocated space according its anchoring.

        :param target_extent: - the amount of space allocated to the drawing

        :return: a private coordinate space for correctly positioning the drawing in the target extent

        :raises: ValueError if the target extent is not large enough to contain the drawing.
        """
        if self.content_size not in target_extent:
            raise ValueError("Expected enough space to draw the diagram!")
        assert isinstance(self.drawing_origin, Pos)
        self._state = States.ready
        # pylint: disable=invalid-unary-operand-type
        origin = self.content_size.anchor_at(self.anchor, target_extent) + (-self.drawing_origin)
        return Region(
            origin, target_extent  # self.content_size  --- should be clipped!
        )

    def draw(self, c: DisplaySurface, region: Region):
        """
        Render my drawing at the request location on the ReportLab display surface <c>.

        :param c: a ReportLab PDF canvas drawing surface to contain the drawing
        :param region: offset + extent into the display surface to position the drawing

        :return: None
        """
        self._state = States.drawn | States.reusable
        if self.drawing is None:
            logging.warning("no diagram to draw!")
            return
        origin: Pos = region.origin
        logging.info("drawing a diagram at (%s, %s)", origin.x.to('in'), origin.y.to('in'))
        assert self.drawing is not None
        renderPDF.draw(self.drawing, c, origin.x.pt, origin.y.pt)
