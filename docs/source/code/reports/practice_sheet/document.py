"""
Kanji Practice Sheet Data
=========================

Support data document for creating a Kanji Practice Sheet

For this report, we need:

    - A kanji drawing server instance to produce SVG stroke diagrams
    - A converter to move from SVG to ReportLab's native graphics format for drawings

In an ideal and future world, the SVG->ReportLab converter would be buried in a technology abstraction layer.
That ideal and future world is not now.

This separation of responsibilities of data vs presentation is close to my final vision for how to describe reports in general.
I see this process as a variant of the model-view-controller design pattern.

.. mermaid::
    :name: cd_practicesheet_data
    :caption: Class relationships for the kanji practice sheet data container.

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
        class Page
        class PageFactory

        <<interface>>RenderingFrame
        RenderingFrame <|-- Container
        Container <|-- Page

        class PracticeSheet
        RenderingFrame <|-- PracticeSheet : realizes
        class PracticeSheetData
        PracticeSheet --* PracticeSheetData : owns this dataset
        PracticeSheet --o PageFactory
        PageFactory ..> Page : produces
        PracticeSheet --* Page : renders its data to here

.. only:: dev_notes

    - Nomenclature: DrawingForRL, RLDrawing to adapter.fromSVG.toRL.Drawing, adapter.fromRL.toSVG.Drawing?

"""
# pylint: disable=fixme

from external_data.kanji_svg import KanjiSVG
from adapter.svg import ReportLabDrawingFactory, DrawingForRL, RLDrawing
from visual.layout.distance import Distance
from visual.layout.region import Extent


# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


def new_image_needed(img, requested_size):
    """
    Experimenting with lazy evaluation for any()... don't take this too seriously.
    """
    def criterion_generator():
        yield img is None
        yield img.width != requested_size.width.pt
        yield img.height != requested_size.height.pt
    return any(criterion_generator())


class PracticeSheetData:
    """
    Document container for the Kanji practice sheet data.

    Note: A "DrawingForRL" instance is a specialized SVG drawing that is friendlier with ReportLab's SVG conversion code than a vanilla SVG
          drawing from the svgwrite module.

    .. mermaid:

        classDiagram
            direction TB
            class SVGDrawing
            class RLDrawing
            class PracticeSheetData
            class KanjiSVG
            class DrawingForRL

            SVGDrawing <|-- DrawingForRL

            class PracticeSheetData {
                +svg_stroke_diagram(int step_columns, Extent size) DrawingForRL
                +svg_practice_strip(int step_columns, Extent size) DrawingForRL
                +stroke_diagram(int step_columns, Extent image_size) -> RLDrawing
                +practice_strip(int step_columns, Extent image_size) -> RLDrawing
            }
            PracticeSheetData : str glyph
            PracticeSheetData : KanjiSVG glyph_svg
            PracticeSheetData *-- KanjiSVG : _glyph_svg
            PracticeSheetData *-- DrawingForRL : _svg_stroke_diagram
            PracticeSheetData *-- DrawingForRL : _svg_practice_strip
            PracticeSheetData *-- RLDrawing : _rl_stroke_diagram
            PracticeSheetData *-- RLDrawing : _rl_practice_strip

    """

    def __init__(self, glyph: str):
        self.glyph = glyph
        self._glyph_svg: KanjiSVG | None = None
        self._svg_stroke_diagram: DrawingForRL | None = None
        self._rl_stroke_diagram: RLDrawing | None = None
        self._svg_practice_strip: DrawingForRL | None = None
        self._rl_practice_strip: RLDrawing | None = None

    # Some instance methods for deferred on-demand data
    # At minimum, we require a glyph, the rest we can get as needed.
    # Review: does thread safety matter?
    @property
    def glyph_svg(self) -> KanjiSVG:
        """
        Provide on-demand instantiation of the GlyphSVG drawing server for our glyph.

        :return: diagram_server - an interface into a kanji stroke diagram server.
        """
        if self._glyph_svg is None:
            assert self.glyph is not None, "Must at least have a glyph for deferred loading of report data"
            glyph_svg = KanjiSVG(self.glyph)
            try:
                glyph_svg.load()
                glyph_svg.drawing_factory = ReportLabDrawingFactory(default_viewbox=glyph_svg.viewbox)
                glyph_svg.stroke_styles["radical"]["stroke"] = 'black'
            except FileNotFoundError as e:
                raise ValueError(f"Error obtaining SVG drawing file for '{self.glyph}'.") from e
            finally:
                self._glyph_svg = glyph_svg
        return self._glyph_svg

    def svg_stroke_diagram(self, step_columns: int, size: Extent) -> DrawingForRL:
        """
        Provide a ReportLab-consumable version of the Kanji's SVG drawing.

        ReportLab is a little touchy about some SVG attributes so we're returning a tweaked SVG
        drawing instance that plays well with ReportLab's svg2rlg() converter function.

        :param step_columns: the maximum number of stroke step diagrams to draw before starting a new row.
        :param size: the desired physical output size. KanjiSVG will map its output viewport to this extent.

        :return: svg_strokes - a step-by-step SVG diagram for stroking our kanji glyph.
        """
        if new_image_needed(self._svg_stroke_diagram, size):
            svg_drawing = self.glyph_svg.draw_stroke_steps(grid_columns=step_columns, cell_size=size)
            assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
            if svg_drawing is None:
                raise ValueError(f"Error generating SVG for '{self.glyph_svg.glyph}'.")
            self._svg_stroke_diagram = svg_drawing
        assert self._svg_stroke_diagram is not None
        return self._svg_stroke_diagram

    def stroke_diagram(self, step_columns: int, image_size: Extent) -> RLDrawing:
        """
        Provide on-demand service of the report lab drawing for our glyph stroke diagram.

        :param step_columns: the maximum number of stroke step diagrams to draw before starting a new row.
        :param image_size: the desired physical output size.

        :return: reportlab_strokes - a step-by-step reportlab-ready diagram for stroking our kanji glyph.
        """
        if new_image_needed(self._rl_stroke_diagram, image_size):
            # Ignore pylint's complaints about no ".inch"
            # pylint: disable=no-member
            svg_drawing = self.svg_stroke_diagram(step_columns, image_size)
            assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
            rlg = svg_drawing.to_RLG()
            if rlg is None:
                raise ValueError(f"Error converting SVG for '{self.glyph_svg.glyph}' to a ReportLab drawing.")
            x1, y1, x2, y2 = b if (b := rlg.getBounds()) else (0, 0, 0, 0)
            logger.info("Created stroke diagram of %s by %s", f'{Distance(x2 - x1, "pt").inch:0.2}', f'{Distance(y2 - y1, "pt").inch:0.2}')
            logger.info(
                "Created stroke diagram bounds = (%s, %s) to (%s, %s)",
                f'{Distance(x1, "pt").inch:0.2}', f'{Distance(y1, "pt").inch:0.2}',
                f'{Distance(x2, "pt").inch:0.2}', f'{Distance(y2, "pt").inch:0.2}'
            )
            self._rl_stroke_diagram = rlg
        assert self._rl_stroke_diagram is not None
        return self._rl_stroke_diagram

    def svg_practice_strip(self, step_columns: int, size: Extent) -> DrawingForRL:
        """
        Provide a ReportLab-consumable version of a lined practice gride to stroke out our kanji glyph.

        ReportLab is a little touchy about some SVG attributes so we're returning a tweaked SVG
        drawing instance that plays well with ReportLab's svg2rlg() converter function.

        :param step_columns: the maximum number of stroke step diagrams to draw before starting a new row.
        :param size: the desired physical output size. KanjiSVG will map its output viewport to this extent.

        :return: svg_practice - a lined practice area divided into cells for drawing kanji
        """
        if new_image_needed(self._svg_practice_strip, size):
            svg_drawing = self.glyph_svg.draw_practice_strip(grid_columns=step_columns, cell_size=size)
            assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
            if svg_drawing is None:
                raise ValueError(f"Error generating practice strip SVG for '{self.glyph_svg.glyph}'.")
            self._svg_practice_strip = svg_drawing
        assert self._svg_practice_strip is not None
        return self._svg_practice_strip

    def practice_strip(self, step_columns: int, image_size: Extent) -> RLDrawing:
        """
        Provide on-demand service of a lined practice gride to stroke out our kanji glyph.

        :param step_columns: the maximum number of stroke step diagrams to draw before starting a new row.
        :param image_size: the desired physical output size.

        :return: reportlab_practice - a lined practice area divided into cells for drawing kanji
        """
        if new_image_needed(self._rl_practice_strip, image_size):
            # Ignore pylint's complaints about no ".inch"
            # pylint: disable=no-member
            svg_drawing = self.svg_practice_strip(step_columns, image_size)
            assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
            rlg = svg_drawing.to_RLG()
            if rlg is None:
                raise ValueError(f"Error converting practice strip SVG for '{self.glyph_svg.glyph}' to a ReportLab drawing.")
            x1, y1, x2, y2 = b if (b := rlg.getBounds()) else (0, 0, 0, 0)
            logger.info("Created practice strip of %s by %s", f'{Distance(x2 - x1, "pt").inch:0.2}', f'{Distance(y2 - y1, "pt").inch:0.2}')
            logger.info(
                "Created practice strip with bounds = (%s, %s) to (%s, %s)",
                f'{Distance(x1, "pt").inch:0.2}', f'{Distance(y1, "pt").inch:0.2}',
                f'{Distance(x2, "pt").inch:0.2}', f'{Distance(y2, "pt").inch:0.2}'
            )
            self._rl_practice_strip = rlg
        assert self._rl_practice_strip is not None
        return self._rl_practice_strip
