"""Adapters from SVG class instances."""


from io import StringIO

from svglib.svglib import svg2rlg, Drawing as RLDrawing
from svgwrite import Drawing as SVGDrawing
from svgwrite.data.types import SVGAttribute
from svgwrite.data.tiny12 import empty_list



class DrawingForRL(SVGDrawing):  # pylint: disable=too-many-ancestors
    """
    A customized version of svgwrite.Drawing for reportlab's svg reader.

    svgwrite is very strict with the SVG standard, but reportlab not-so-much.
    This is were we'll reconcile these differences of opinion.

    Our initializer bypasses the Drawing initializer to prevent unwanted XML attributes:
            - xmlns:xlink
            - xmlns:ev
            - version
            - baseProfile
    on the SVG tag.  We also intercept the size and viewBox keywords out of **kwargs to
    to prevent unwanted 'height' and 'width' attributes and to force svgwrite to accept
    length parameters for the 'viewBox' attribute.

    Finally, we'll put the xmlns namespace back on the SVG tag.
    """

    def __init__(self, *args, size: tuple[str, str] | None = None, viewBox: str | None = None, **kwargs):
        """Force the svgwrite data validator to accept length parameters for the viewBox attribute."""
        super().__init__(*args, **kwargs)
        self.validator.attributes['viewBox'] = SVGAttribute('viewBox', anim=True, types=frozenset(['list-of-length']),  const=empty_list)
        if viewBox:
            self.attribs['viewBox'] = viewBox
        # If I did not pass a size, do not give it a size!
        if not size:
            del self.attribs['height']
            del self.attribs['width']
        else:
            width, height = map(str, size)
            self.attribs['height'] = height
            self.attribs['width'] = width
        # Put this back
        self.attribs['xmlns'] = "http://www.w3.org/2000/svg"

    def get_xml(self):
        """
        Intercept the get_xml method to prevent the Drawing class from adding unwanted XML attributes.

        This method is only used internally by svgwrite; this override is my hook into svgwrite's internals
        where I can suppress (or not) individual tags.
        """
        return super(SVGDrawing, self).get_xml()

    def to_RLG(self) -> RLDrawing | None:  # pylint: disable=invalid-name
        """Convert the drawing to ReportLab Graphics (RLG)."""
        xml_string = StringIO(self.tostring())
        return svg2rlg(xml_string)


class ReportLabDrawingFactory:  # pylint: disable=too-few-public-methods
    """Build an svgwrite.Drawing instance that is compatible with ReportLab."""

    def __init__(self, default_viewbox):
        self.default_viewbox = default_viewbox

    def __call__(self, *args, viewbox = None, viewBox = None, **kwargs) -> DrawingForRL:
        viewbox = viewbox or viewBox
        if not viewbox:
            viewbox = self.default_viewbox
        return DrawingForRL(*args, viewBox=viewbox, **kwargs)
