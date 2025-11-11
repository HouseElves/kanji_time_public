# document.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Kanji Summary Sheet Data
========================

Support data document for creating a Kanji Practice Sheet

For this report, we need:

    - A kanji drawing server instance to produce SVG stroke diagrams
    - A radical service to get descriptive content for a kanji radical
    - A dictionary service (really two services) to get definition content for a kanji glyph
    - Reportlab text services
    - A converter to move from SVG to ReportLab's native graphics format for drawings

In an ideal and future world, all of the ReportLab details would be buried in a technology abstraction layer.
That ideal and future world is not now.

I see my reporting model as a variant of the model-view-controller design pattern.
This is the "model" portion of that pattern for the Kanji Summary Sheet report.

.. mermaid::
    :name: cd_infosheet_data
    :caption: Class relationships for the kanji information report data container.

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

        class KanjiReport
        RenderingFrame <|-- KanjiReport : realizes
        class KanjiReportData
        PracticeSheet --* KanjiReportData : owns this dataset
        PracticeSheet --o PageFactory
        PageFactory ..> Page : produces
        KanjiReport --* Page : renders its data to here

"""
# pylint: disable=fixme

import dataclasses
from collections.abc import Sequence
from typing import Any
from itertools import zip_longest
import logging

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab import rl_config

from kanji_time.utilities.general import coalesce_None, flatten
from kanji_time.utilities.xml import in_bold, in_italic, in_typeface
from kanji_time.adapter.svg import DrawingForRL, RLDrawing, ReportLabDrawingFactory
from kanji_time.external_data import kanji_dic2 as kanji_dict2, kanji_dict
from kanji_time.external_data.kanji_svg import KanjiSVG
from kanji_time.external_data.radicals import Radical
from kanji_time.visual.layout.region import Extent


logger = logging.getLogger(__name__)
rl_config.allowTableBoundsErrors = True


def required():
    """Force explicit initializer values to the below dataclass."""
    assert False, "This is a required field."


@dataclasses.dataclass
class KanjiReportData:
    """
    Model a "document" for a KanjiReport "view".

    A kanji information report requires:

        - a Unicode kanji glyph
        - the radical number assigned to the kanji
        - ReportLab drawing instances for the large kanji and small radical vector graphics
        - HTML-like formatted text for

            - "banner" |rarr| simple kanji meaning, readings, frequency
            - "radical" |rarr| radical number, romanji/hiragana name, interpretation
            - "body" |rarr| full dictionary definition with reading and frequency for each sense of the kanji
            - "page2on" |rarr| short banner text for after the first page

    Most of this dataclass consists of helper functions go get specific data items on demand.

    .. only:: dev_notes

        - the interaction between the ReportLab rendering technology and the data needs to be decoupled.
        - is the data acquisition thread safe?
        - need a mechanism to push/pop styles - see the @styled concept in the dev notes page
        - what about fall-back behavior when

            - I can't get an SVG drawing?
            - I can't get details about a radical?  (is KanjiSVG useful as a fallback from dict2?)

        - the `get_radical_svg_drawing_method` draws the radical strokes exactly where they are in the glyph.
          I.e, it's like drawing the glyph w/ the non-radical strokes invisible.  Can/should I make a version of this that positions the
          radical strokes only in the drawing area?

    """

    glyph: str
    glyph_svg: KanjiSVG = dataclasses.field(default_factory=required)
    banner_kanji: RLDrawing = dataclasses.field(default_factory=required)
    radical_kanji: RLDrawing = dataclasses.field(default_factory=required)
    text: dict[str, Sequence[Paragraph]] = dataclasses.field(default_factory=dict)
    radical_num: int = 0

    # Some instance methods for deferred on-demand data
    # At minimum, we require a glyph, the rest we can get as needed.
    # Review: is thread safety an issue?
    @property
    def _glyph_svg(self):
        """Provide on-demand instantiation of the GlyphSVG drawing server for our glyph."""
        if self.glyph_svg is None:
            assert self.glyph is not None, "Must at least have a glyph for deferred loading of report data"
            self.glyph_svg = self.get_glpyh_svg(self.glyph)
        return self.glyph_svg

    def get_reportlab_glyph(self, image_size: Extent):
        """Provide on-demand service of the report lab drawing for our glyph."""
        def rebuild_image():
            """Experimenting with lazy evaluation for any()... don't take this too seriously."""
            yield self.banner_kanji is None
            yield self.banner_kanji.width != image_size.width.pt
            yield self.banner_kanji.height != image_size.height.pt
        if any(rebuild_image()):
            self.banner_kanji = self.get_glyph_reportlab_drawing(self._glyph_svg, image_size)
        return self.banner_kanji

    def get_reportlab_radical(self, image_size: Extent):
        """Provide on-demand service of the report lab drawing for our glyph's radical."""
        def rebuild_image():
            """Experimenting with lazy evaluation for any()... don't take this too seriously."""
            yield self.radical_kanji is None
            yield self.radical_kanji.width != image_size.width.pt
            yield self.radical_kanji.height != image_size.height.pt
        if any(rebuild_image()):
            self.radical_kanji = self.get_radical_reportlab_drawing(self._glyph_svg, image_size)
        return self.banner_kanji

    @classmethod
    def get_glpyh_svg(cls, glyph: str) -> KanjiSVG:
        """Load up the SVG file for the glyph and set the radical strokes to black."""
        glyph_svg = KanjiSVG(glyph)
        try:
            glyph_svg.load()
        except FileNotFoundError as e:
            raise ValueError(f"No SVG drawing file for '{glyph}'.") from e
        finally:
            glyph_svg.drawing_factory = ReportLabDrawingFactory(default_viewbox=glyph_svg.viewbox)
            glyph_svg.stroke_styles["radical"]["stroke"] = 'black'  # need a style context manager push/pop
        return glyph_svg

    @classmethod
    def get_glyph_svg_drawing(cls, glyph_svg: KanjiSVG, size: Extent) -> DrawingForRL:
        """
        Provide a ReportLab-consumable version of the Kanji's SVG drawing.

        ReportLab is a little touchy about some SVG attributes so we're returning a tweaked SVG
        drawing instance that plays well with ReportLab's svg2rlg() converter function.

        :param glyph_svg: - SVG server for a particular Kanji or kana glyph.
        :param size: - the desired physical output size. KanjiSVG will map the viewport to this extent to convert internal coordinates.
        """
        svg_drawing = glyph_svg.draw_glyph(
            no_center=True,
            image_size=size
        )
        # Consider technology behaviors like "SupportsReportLab[P]" where P is a protocol?
        assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
        if svg_drawing is None:
            # I need a better fallback position:  a text glyph?
            raise ValueError(f"Error generating SVG for '{glyph_svg.glyph}'.")
        assert isinstance(svg_drawing, DrawingForRL)
        return svg_drawing

    @classmethod
    def get_glyph_reportlab_drawing(cls, glyph_svg: KanjiSVG, size: Extent) -> RLDrawing:
        """
        Provide a ReportLab formatted RLG version of the Kanji's radical's SVG drawing.

        :param glyph_svg: - SVG server for a particular Kanji or kana glyph.
        :param size: - the desired physical output size. KanjiSVG will map the viewport to this extent to convert internal coordinates.
        """
        svg_drawing = cls.get_glyph_svg_drawing(glyph_svg, size)
        assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
        rlg = svg_drawing.to_RLG()
        if rlg is None:
            raise ValueError(f"Error converting SVG for '{glyph_svg.glyph}' to a ReportLab drawing.")
        return rlg

    @classmethod
    def get_radical_svg_drawing(cls, glyph_svg: KanjiSVG, size: Extent) -> DrawingForRL:
        """
        Provide a ReportLab-consumable version of the Kanji's radical's SVG drawing.

        ReportLab is a little touchy about some SVG attributes so we're returning a tweaked SVG
        drawing instance that plays well with ReportLab's svg2rlg() converter function.

        :param glyph_svg: - SVG server for a particular Kanji or kana glyph.
        :param size: - the desired physical output size. KanjiSVG will map the viewport to this extent to convert internal coordinates.

        """
        # Should the radical take up the entire drawing frame?  I.e. parse out the size of just the radical strokes?
        # The current draw technique does have the feature of positioning the radical exactly where it is in the full glyph.
        radical_precedence = ["tradit", "general", "jis", "nelson"]
        radical = next((radical for radical in radical_precedence if radical in glyph_svg.radical_strokes), None)
        if radical is None:
            logger.warning("No radical defined for %s.", glyph_svg.glyph)
        svg_drawing = glyph_svg.draw_glyph(
            radical=radical,
            no_center=True,
            radical_only=True,
            image_size=size
        )
        assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
        if svg_drawing is None:
            # I need a better fallback position:  a text glyph?  Unicode has all the radicals and variants.
            raise ValueError(f"Error generating SVG for '{glyph_svg.glyph}'\'s radical.")
        assert isinstance(svg_drawing, DrawingForRL)
        return svg_drawing

    @classmethod
    def get_radical_reportlab_drawing(cls, glyph_svg: KanjiSVG, size: Extent) -> RLDrawing:
        """
        Provide a ReportLab formatted RLG version of the Kanji's radical's SVG drawing.

        :param glyph_svg: - SVG server for a particular Kanji or kana glyph.
        :param size: - the desired physical output size. KanjiSVG will map the viewport to this extent to convert internal coordinates.
        """
        # Should the radical take up the entire drawing frame?  I.e. parse out the size of just the radical strokes?
        svg_drawing = cls.get_radical_svg_drawing(glyph_svg, size)
        assert isinstance(svg_drawing, DrawingForRL), "Expected ReportLab support in the Drawing instance."
        rlg = svg_drawing.to_RLG()
        if rlg is None:
            raise ValueError(f"Error converting SVG for '{glyph_svg.glyph}'\'s radical to a ReportLab drawing.")
        return rlg

    @classmethod
    def get_glyph_detail(cls, glyph: str) -> dict[str, Any]:
        """Provide a dictionary details about the Kanji glyph <glyph>."""
        flat_xml: dict[str, Any] = {}
        flat_xml["dict2"] = [
            kanji_dict2.flatten_xml(glyph_xml)
            for glyph_xml in kanji_dict2.get_glyph_xml(glyph)
        ]

        radical_details = []
        for dict2 in flat_xml["dict2"]:
            radical_num = coalesce_None(dict2, 'kangxi radical', 'Unknown')
            assert isinstance(radical_num, str)
            radical_details.append(Radical(radical_num) if radical_num != 'Unknown' else None)
        flat_xml['radical_details'] = radical_details  # I can get the radical out of the SVG as a fallback.  But what's the point?

        flat_xml["dict"] = [
           kanji_dict.flatten_xml(glyph_xml)
           for glyph_xml in kanji_dict.get_glyph_xml(glyph)
        ]

        empty = [key for key, value in flat_xml.items() if not value]
        if empty:
            logger.warning("No glyph details in %s for %s.", ', '.join(empty), glyph)

        return flat_xml

    @classmethod
    def format_banner_text(cls, styles, kanji_detail) -> Sequence[Paragraph]:
        """Provide a summary about the kanji glyph described by <kanji_detail>."""
        # Doesn't look like pylint understands the walrus very well. It's OK. The walrus was Paul.
        # pylint: disable=used-before-assignment
        banner_text = [
            Paragraph(
                f"{', '.join(m) if (m := kanji_detail.get('meanings', None)) is not None else 'Unknown Meaning'}"
                "<br/>",
                styles['English Title']
            ),
            Paragraph(
                f"{in_typeface('Helvetica', in_bold('Kun readings: '))}"
                f"{', '.join(kun) if (kun := kanji_detail['kun_readings']) is not None else 'Unknown kun?'}",
                styles['Japanese Definition']
            ),
            Paragraph(
                f"{in_typeface('Helvetica', in_bold('On readings: '))}"
                f"{', '.join(on) if (on := kanji_detail['on_readings']) is not None else 'Unknown on?'}",
                styles['Japanese Definition']
            ),
            Paragraph(
                in_typeface(
                    'Helvetica',
                    in_bold('Frequency Ranking: ') + (','.join(f) if (f := kanji_detail['frequency']) is not None else 'unknown')
                ),
                styles['Japanese Definition']
            ),
        ]
        return banner_text

    @classmethod
    def format_page2on_text(cls, styles, kanji_detail) -> Sequence[Paragraph]:
        """Provide a summary about the kanji glyph described by <kanji_detail>."""
        # Doesn't look like pylint understands the walrus very well. It's OK. The walrus was Paul.
        # pylint: disable=used-before-assignment
        page2on_text = [
            Paragraph(
                f"{', '.join(m) if (m := kanji_detail.get('meanings', None)) is not None else 'Unknown Meaning'}",
                styles['English Title']
            ),
            Paragraph(in_italic("continued"), styles['English Title']),
        ]
        return page2on_text

    @classmethod
    def format_radical_text(cls, styles, radical_detail) -> Sequence[Paragraph]:
        """Provide a summary about the radical in the kanji glyph described by <kanji_detail>."""
        glyphs = ", ".join(radical_detail.glyphs)
        name = ", ".join(radical_detail.hiragana_names)
        meaning = ", ".join(radical_detail.interpretations)
        romanji = radical_detail.romanji_name

        radical_text: Sequence[Paragraph] = [
            Paragraph(
                in_typeface('Helvetica', f'Radical #{radical_detail.radical_num}: ') + f"{glyphs}", styles['Japanese Align=Right']
            ),
            Paragraph(name + '<br/>' if name is not None else '', styles['Japanese Align=Right']),
            Paragraph(in_typeface('Helvetica', romanji) + '<br/>' if romanji is not None else '', styles['Japanese Align=Right']),
            Paragraph(in_typeface('Helvetica', meaning), styles['Japanese Align=Right']),
        ]

        return radical_text

    @classmethod
    def format_body_text(cls, styles, kanji_iterpretation) -> Sequence[Paragraph]:
        """Provide a detailed formatted description of kanji glyph described by <kanji_interpretation>."""
        face = "HeiseiMin-W3"
        delim = f'</font>, <font face={face}>'

        body_text = flatten([
            [
                Paragraph(f"Glyphs {j+1}: {in_typeface(face, delim.join(md['glyph']))}", styles['Heading1']),
                Paragraph(f"<b>Frequency: </b>{', '.join(md['frequency'])}" if md['frequency'] else "", styles['Normal']),
                Paragraph(f"<b>Readings: </b>{in_typeface(face, delim.join(md['readings']))}", styles['Normal']),
                [
                    [
                        # collect these into "no orphans"-paragraph formatted text frames.
                        # Maybe "no orphans" is just a paragraph style?
                        Paragraph(f"Sense {j+1}.{i+1}", styles['Heading2']),
                        Paragraph(f"\t<b>POS: </b>{', '.join(s['pos'])}", styles['Normal']),
                        Paragraph(f"\t<b>Misc: </b>{', '.join(s['misc'])}" if s['misc'] else "", styles['Normal']),
                        Paragraph(f"\t<b>Meaning: </b>{'; '.join(s['gloss'])}", styles['Normal']),
                        Paragraph("<br/>", styles['Heading1']),
                    ]
                    for i, s in enumerate(md['senses'])
                ]

            ]
            for j, md in enumerate(kanji_iterpretation)
        ])

        return body_text


def build_data_object(glyph: str, size: Extent) -> KanjiReportData:
    """
    Model the "document" for a a report "view" on our Kanji database.

    This data object specifically models the data for a kanji summary report.

    :param glyph: - the kanji glyph for which to obtain data
    :param size: - requested size for the ReportLab drawings of the kanji

    :return: a dataclass-like instance containing all the necessary information to construct a Kanji Summary report.

    ..only:: dev_notes

        - should I be passing <size> into this function?  I feel that vector graphics shouldn't need this and that
          the Drawing RenderingFrame implementation should supply it on demand.  See notes about <size> parameters in
          `external_data.kanji_svg.KanjiSVG.draw_stroke_steps` et al.
        - oof! the style needs to be in an options, not hardcoded
        - BIG: reconcile the big block of details from KanjiDict against multiple entries in KanjiDict2.?
          I am only taking the _first_ from zip_longest(kanji_details, radical_details).
    """

    try:
        glyph_svg: KanjiSVG = KanjiReportData.get_glpyh_svg(glyph)
        banner_kanji: RLDrawing = KanjiReportData.get_glyph_reportlab_drawing(glyph_svg, size)
        radical_kanji: RLDrawing = KanjiReportData.get_radical_reportlab_drawing(glyph_svg, size//2)
        glyph_detail: dict[str, Any] = KanjiReportData.get_glyph_detail(glyph)
    except Exception as e:
        # need some kind of reasonable fallback.  A 288pt character? :-)
        # Issue:  on real failure, I should skip insetead of abort --> well, make that configurable.
        logging.info("Could not obtain graphics for %s: %s", glyph, e)
        raise e

    text: dict[str, Sequence[Paragraph]] = {}

    styles = {
        # persist this in an options thingy somewhere & load it at runtime instead of hardcoding.
        'Normal': getSampleStyleSheet()['Normal'],
        'Heading1': getSampleStyleSheet()['Heading1'],
        'Heading2': getSampleStyleSheet()['Heading2'],
        'English Title': ParagraphStyle(
            'English Title',
            alignment=1, fontName='Helvetica-Bold', fontSize=14, leading=17
        ),
        'English Align=Right': ParagraphStyle(
            'English Align=Right',
            alignment=2, fontName='Helvetica', fontSize=10, leading=13
        ),
        'Japanese Definition': ParagraphStyle(
            'Japanese',
            fontName='HeiseiMin-W3', fontSize=10, leading=13, firstLineIndent=-18, leftIndent=18
        ),
        'Japanese Align=Right': ParagraphStyle(
            'JapaneseRight',
            alignment=2, fontName='HeiseiMin-W3', fontSize=10, leading=13
        ),
    }


    # Issue: how do I reconcile the big block of details from KanjiDict against multiple entries in KanjiDict2?
    #
    # This is important to pagination.  Perhaps the glyphs are the key?
    # Having the body text outside the zip() without some kind of join/reconciliation is going to cause me grief
    # in the future when I expand this for loop to all the glyph detail from KanjiDict2

    kanji_details: list[dict[str, Any]] = glyph_detail["dict2"] if glyph_detail["dict2"] else []
    radical_details: list[Radical] = glyph_detail["radical_details"] if glyph_detail["radical_details"] else []
    radical_num = 0

    for (kanji_detail, radical_detail) in zip_longest(kanji_details, radical_details):
        text["banner"] = KanjiReportData.format_banner_text(styles, kanji_detail) if kanji_detail else []
        text["radical"] = KanjiReportData.format_radical_text(styles, radical_detail) if radical_detail else []
        text["page2on"] = KanjiReportData.format_page2on_text(styles, kanji_detail) if kanji_detail else []
        radical_num = radical_detail.radical_num if radical_detail else 0
        break  # only get the first one.

    kanji_iterpretation = glyph_detail["dict"]
    if not kanji_iterpretation:
        logger.warning("No KanjiDict record for glyph '%s'", glyph)

    text["body"] = KanjiReportData.format_body_text(styles, kanji_iterpretation) if kanji_iterpretation else []

    return KanjiReportData(
        glyph, glyph_svg,
        banner_kanji, radical_kanji,
        text,
        radical_num
    )
