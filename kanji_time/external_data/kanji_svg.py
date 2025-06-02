"""
Model SVG drawings of Kanji characters.

The Kanji vector graphics SVG files are are copyright © 2009-2024 Ulrich Apel & used under the
`Creative Commons Attribution-Share Alike 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>`_ license.
Original SVG content is located `here <https://kanjivg.tagaini.net/>_`.

These Kanji SVG files are used and redistributed unaltered.

Licensing/Credits:
    - The KanjiTime program and all its code is copyright (c) 2024-2025 by Andrew Milton (HouseElves).
    - The underlying SVG files released under the Creative Commons Attribution-Share Alike 3.0 license

----

.. seealso:: :doc:`dev_notes/kanji_svg_notes`

----

 """
# pylint: disable=fixme

import copy
from itertools import product
import threading

from typing import Any, cast
from functools import cache

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

from IPython.display import SVG, display
from svgwrite import Drawing as SVGDrawing

from kanji_time.svg_transform import Transform
from kanji_time.external_data import settings
from kanji_time.utilities.general import log
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent


# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


# Define a factory function type for producing svgwrite.Drawing instances from arbitrary inputs.
#
#: Drawing factories produce svgwrite.Drawing instances compatible with our client's rendering technology.
#: The client passes a DrawingFactory instance that it creates into the Kanji SVG drawing server initializer.
DrawingFactory = Callable[..., SVGDrawing]


def default_drawing_factory(*args, **kwargs) -> SVGDrawing:
    """
    Create an ordinary SVG drawing object instance.

    Clients may provide an alternate factory that yields some subclass instance of
    svgwrite.Drawing so they can provide any necessary specialized adapter logic
    for their particular rendering technology.

    :param args, kwargs: pass-through positional and keyword arguments to the svgwrite.Drawing initializer.
    :return: an svgwrite.Drawing instance.
    """
    return SVGDrawing(*args, **kwargs)


class SVGCache(type):
    """
    A metaclass to cache Kanji_SVG kanji stroke drawing service instances.

    The caching functionality is very primitive: it's POC for the approach.
    A 'cached dict' that exploits @lru_cache would be more appropriate
    instead of the vanilla dict for <_cache> below.

    :param glyph: the kanji Unicode codepoint
    :param no_cache: "create only" when true - forces creating a fresh drawing service instance for the glyph and does not cache it.

    .. only:: dev_notes

        - Make a generic version to cache instances as singletons.
          This will need list of int/str for parameters for caching
          Maybe even an xform function to make them hashable
        - Explore the concept of a `cached_dict` type exploiting @lru_cache

    """
    _lock: threading.Lock = threading.Lock()
    _cache: dict[str, 'KanjiSVG'] = {}

    def __call__(cls, glyph: str, no_cache: bool = False):
        """Intercept the construction function to redirect to the cache."""
        if no_cache:
            instance = super().__call__(glyph)
            assert glyph not in cls._cache or cls._cache[glyph] != instance
            logger.info("%s created a unique KanjiSVG for '%s', returning id=%s", cls.__name__, glyph, f"{id(cls._cache[glyph]):x}")
            return instance

        result = "hit"
        if glyph not in cls._cache:
            # threads might race to the lock so check again inside...
            with cls._lock:
                if glyph not in cls._cache:  # ...to resolve possible race condition
                    result = "miss"
                    instance = super().__call__(glyph)
                    cls._cache[glyph] = instance
                else:  # pragma: no branch
                    logger.info("trapped race condition on glyph %s.", glyph)  # pragma: no cover
        logger.info("%s %s for '%s', returning id=%s", cls.__name__, result, glyph, f"{id(cls._cache[glyph]):x}")
        return cls._cache[glyph]


class KanjiSVG(metaclass=SVGCache):
    """
    A drawing service for kanji strokes using the scalable Kanji SVG project data.

    This service uses scalable vector graphics files from the Kanji SVG project, located at https://kanjivg.tagaini.net/.
    These files are copyright © 2009-2024 Ulrich Apel released under the Creative Commons Attribution-Share Alike 3.0 license.

    :param glyph: the Unicode codepoint for which we want a drawing service.
    :param drawing_factory: constructor for svgwrite.Drawing instances that are possibly specialized for the client's rendering technology.

    .. only:: dev_notes

        - the loader needs to be broken out from the draw logic w/ general XML handling factored out.
        - review the DFLT_GLYPH_SIZE -- should it even be in here?  make it a global constant?

    .. mermaid::
        :name: cd_kanjisvg
        :caption: Class relationships for the kanji drawing service.

        ---
        config:
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
            class StrokeDictionary
            class NamespaceMap
            class DrawingFactory{
                +__call__(*args, **kwargs) SVGDrawing
            }

            class Kanji_SVG {
                +str glyph
                +bool loaded
                +Pos center
                +str viewbox


                +load()
                +draw_glyph(str radical_name, bool radical_only, bool no_center, Extent image_size) SVGDrawing
                +draw_stroke_steps(int grid_columns, Extent cell_size) SVGDrawing
                +draw_practice_strip(int grid_columns, Extent cell_size) SVGDrawing

                -compute_layout(Distance cell_width, int cell_count, Distance cell_height) tuple
                -draw_strokes(SVGDrawing drawing, Iterable[int] stroke_range, dict[str, Any] style, Transform transform, bool with_labels = False)
                -draw_practice_axes(SVGDrawing drawing, tuple[int, int] cell_count, int cell_px_width, int cell_px_height)
                -draw_cell_dividers(SVGDrawing drawing, tuple[int, int] cell_count, int cell_px_width, int cell_px_height)
            }
            Kanji_SVG --o DrawingFactory : drawing_factory
            Kanji_SVG --* "m" Group : _groups
            Kanji_SVG --* "n" Stroke : strokes
            Kanji_SVG --* "n" Label : _labels
            Kanji_SVG --* StrokeDictionary : radical_strokes
            Kanji_SVG --* NamespaceMap : xml_namespace
    """

    #: The default size for a drawn kanji glyph's bounding box.
    #:
    #: .. only:: dev_notes
    #:
    #:      - is this necessary still?
    #:
    DFLT_GLYPH_SIZE = Extent(Distance(2, "in"), Distance(2, "in"))

    @dataclass
    class StrokeGroup:
        """
        Represent a Kanji SVG "svg.g" XML element containing a named collection of kanji strokes as a dataclass.

        The data member descriptions below are summarized from https://kanjivg.tagaini.net/svg-format.html.

        :param id: Unique identifier for the group of the form "<Unicode cp in hex>" for the top-most group
            or "<Unicode cp in hex>-g<n>" for subgroups, where <n> is the 1-based sequence number.
        :param element: The Unicode character that best resembles the result of drawing the strokes in the group.
            For the topmost group, this is the CJK Unified Ideograph codepoint for the complete Kanji.
        :param variant: Indicates that the strokes form a non-standard representation of <element>
        :param partial: Indicates that there are more strokes for this group than present in this XML element.
        :param original:  The Unicode codepoint for the semantic interpretation of the stroke group when it is
            distinct from the the drawn representation.
        :param part: The sequentially numbered continuation of a group when the group's strokes are not contiguous.
        :param number: The sequentially numbered continuation of a subgroup when the subgroup's strokes are not contiguous.
        :param tradForm: The traditional Kanji radical.
        :param radicalForm: Indicates that the radical-like form of a character described by <original> is provided as the <element>.
        :param position: The positioning of the stroke group within the Kanji
        :param radical: The name of the radical set for which the group might belong
        :param phon: Marks groups that may be part of the "phonetic" part of the Kanji - this is wildly inconsistent.

        .. only:: dev_notes

            - extract the XML specific logic to a collection of XML utilities.

        """
        # member names derive from the DTD which uses camelCase
        # I'm keeping them the same for consistency.
        id: str
        element: str = field(default='')
        variant: str = field(default='')
        partial: str = field(default='')
        original: str = field(default='')
        part: str = field(default='')
        number: str = field(default='')
        tradForm: str = field(default='')  # pylint: disable=invalid-name
        radicalForm: str = field(default='')  # pylint: disable=invalid-name
        position: str = field(default='')
        radical: str = field(default='')
        phon: str = field(default='')

        @classmethod
        @property
        @cache
        def attrib_namespace(cls):
            """
            Map full XML attribute Q-names to our internal data member names.

            Names not in this dictionary will not be accepted in the instance initializer.
            """
            return {
                ET.QName('http://kanjivg.tagaini.net', 'element').text: 'element',
                ET.QName('http://kanjivg.tagaini.net', 'number').text: 'number',
                ET.QName('http://kanjivg.tagaini.net', 'original').text: 'original',
                ET.QName('http://kanjivg.tagaini.net', 'part').text: 'part',
                ET.QName('http://kanjivg.tagaini.net', 'partial').text: 'partial',
                ET.QName('http://kanjivg.tagaini.net', 'phon').text: 'phon',
                ET.QName('http://kanjivg.tagaini.net', 'position').text: 'position',
                ET.QName('http://kanjivg.tagaini.net', 'radical').text: 'radical',
                ET.QName('http://kanjivg.tagaini.net', 'radicalForm').text: 'radicalForm',
                ET.QName('http://kanjivg.tagaini.net', 'tradForm').text: 'tradForm',
                ET.QName('http://kanjivg.tagaini.net', 'variant').text: 'variant',
            }
        @classmethod
        def from_element(cls, element: ET.Element):
            """
            Construct an instance of this dataclass from an XML element's attributes.

            :param element: the XMK element instance to scan for attributes in my namespace.
            """
            return cls(**dict((cls.attrib_namespace.get(a, a), b) for (a, b) in element.items()))

    @dataclass
    class Stroke:
        """
        Represent a Kanji SVG XML element for a single kanji stroke.

        The data member descriptions below are summarized from https://kanjivg.tagaini.net/svg-format.html.

        :param id: Unique identifier for the stroke of the form "<Unicode codepoint in hex>-s<n>", where <n> is
            the 1-based sequence number.
        :param d: The SVG path that describes how to draw the stroke.
        :param type: A rough classification string token for the stroke by the stroke's general shape.
        """
        id: str
        d: str
        type: str

        @classmethod
        @property
        @cache
        def attrib_namespace(cls):
            """
            Map full XML attribute Q-names to our internal data member names.

            Names not in this dictionary will not be accepted in the instance initializer.
            """
            return {ET.QName('http://kanjivg.tagaini.net', 'type').text: 'type'}

        @classmethod
        def from_element(cls, element: ET.Element):
            """
            Construct an instance of this dataclass from an XML element's attributes.

            :param element: the XMK element instance to scan for attributes in my namespace.
            """
            return cls(**dict((cls.attrib_namespace.get(a, a), b) for (a, b) in element.items()))

    # According to Pylint, literals are up to 18% faster than calling dict() to construct my dictionaries.
    # See https://pylint.pycqa.org/en/latest/user_guide/messages/refactor/use-dict-literal.html

    #: SVG styles to apply to individual kanji stokes keyed by stroke type
    #:
    #:     - completed - a stroke appearing in a prior step of a step-by-step stroke sequence
    #:     - next - a stroke appearing for the first time as the current step of a step-by-step stroke sequence
    #:     - radical - a stroke appearing as part of a radical group
    #:
    stroke_styles = {
        "completed": {
            'fill': "none",
            'stroke': "black",
            'stroke_width': 2,
        },
        "next": {
            'fill': "none",
            'stroke': "red",
            'stroke_width': 2,
        },
        "radical": {
            'fill': "none",
            'stroke': "blue",
            'stroke_width': 2,
        }
    }
    #: SVG style for all numerical stroke order labels
    label_style = {
        'font_size': "8pt",
        'text_anchor': "middle",
        'fill': "red"
    }
    #: SVG style for practice grid lines
    practice_line_style = {
        'stroke': "silver",
        'stroke_dasharray': "5,5",
    }
    #: SVG style for cell borders delimited each step in a stroke order diagram
    cell_border_style = {
        'stroke': "grey",
        'fill': "none",
        'stroke_width': 2
    }

    def __init__(self, glyph: str, drawing_factory: DrawingFactory = default_drawing_factory):
        """
        Initialize a Kanji SVG drawing server instance for a particular glyph.

        The optional drawing factory parameter can be passed in by clients that need to have
        special handling for SVG drawing above that provided in the <svgwrite> module.
        """
        self.glyph = glyph
        self.drawing_factory = drawing_factory
        self.loaded = False
        self.min_x, self.min_y, self.width, self.height = 0, 0, 0, 0
        self._strokes: list[str] = []
        self._labels = []
        self._groups = {}
        self.strokepaths_id = f"StrokePaths_{ord(glyph):05x}"
        self.labels_id = f"StrokeNumbers_{ord(glyph):05x}"
        self.topmost_id = f"{ord(glyph):05x}"
        self.child_id_prefix = f"{ord(glyph):05x}-g"
        self.stroke_id_prefix = f"{ord(glyph):05x}-s"
        self.namespace = {
            "svg": "http://www.w3.org/2000/svg",
            "kvg": "http://kanjivg.tagaini.net"
        }
        self.radical_strokes = defaultdict(list)

    def _load_all_groups(self, topmost_group_maybe: ET.Element | None) -> list[str]:
        """
        Build a tree structure of stroke groups and strokes.

        We build the tree using a non-recursive breadth first traversal of the kanji stroke group XML nodes.

        :param group_element: top-most group tag of the Kanji SVG stokes
        :param group_attribs: Kanji SVG XML attributes of <group_element>

        :return: The list of all the strokes in the kanji across all groups.

        .. only:: dev_notes

            - add strict type aliases for special purpose strings: SVG commands, Kanji parts, etc.
            - do QNames belong with their associated dataclass as an attribute?
              can I do this with an @XML decorator on top of @dataclass?
            - add cleaning logic to the Stroke post_init?  Maybe by XML parameter name?
            - is a Maybe[T] = {Just[T], Nothing} worth it coupled to the new matching features of Python?
            - shouldn't be setting self._groups directly in this method - need a way to pass the groups back
            - need to create a dispatch dictionary associating tags to tag handlers to clean this up a bit
            - do the completed_{attribs, groups} audit sets need to be distinct?

        """
        # make these class attributes along with self.namespace?  An XML decorator?
        path_tag =  ET.QName(self.namespace['svg'], 'path').text
        group_tag = ET.QName(self.namespace['svg'], 'g').text
        radical_attrib = ET.QName(self.namespace['kvg'],'radical').text

        # Nothing to do if we don't have a root stroke group
        # My mechanism for passing this in as a maybe is sketchy - I've been thinking about "Maybe" wrappers.
        #       Maybe<T> with Just(<value>) and Nothing
        if topmost_group_maybe is None:
            return []
        topmost_group: ET.Element = cast(ET.Element, topmost_group_maybe)

        strokes: list[tuple[int, str]] = []  # a dict keyed on stroke number instead?

        # There can be multiple radicals identified in a kanji depending on who identified the radicals.
        # Convert the radical name attribute to a set to handle this gracefully.
        group_attribs: Mapping[str, Any] = dict(topmost_group.items())
        if radical_attrib in group_attribs:
            group_attribs[radical_attrib] = {group_attribs[radical_attrib]}
        self._groups[group_attribs["id"]] = group_attribs  # return a groups dict, don't directly set the instance attribute

        #: string id -> int converter for stroke numbers
        extract_stroke_number = lambda x: int(x[x.index(':')+len(self.stroke_id_prefix)+1:])

        # Do a breadth first traversal of the kanji stroke groups
        #
        queue = [(topmost_group, group_attribs)]
        completed_attribs, completed_groups = set(), set()
        while queue:
            current_group, current_attribs = queue.pop(0)
            # we should only see each (group, attribs) pair once: setting attribute keys is expected behavior here.
            # OTOH, clobbering a key on a second visit is bad behavior.
            assert id(current_attribs) not in completed_attribs, "Unexpected revisit to a group attribute set"
            current_attribs["strokes"] = []
            current_attribs["groups"] = []

            # make sure that we're not walking a group multiple times
            assert id(current_group) not in completed_groups, "Unexpected revisit to a group"
            for element in current_group:
                # these tag handlers should be in a dispatch dictionary
                # something like "data_object, discovered_elements = load_handler[tagname](element, context)"
                if element.tag == path_tag:
                    # Add an SVG stroke path
                    stroke = dict(element.items())
                    _s = self.__class__.Stroke.from_element(element)  # just a test, will replace "stroke = dict(element.items())"
                    stroke['d'] = stroke['d'].replace("-", " -")  # Normalize negative signs - add cleaning logic to the Stroke post_init?
                    stroke['group'] = current_attribs['id']
                    current_attribs["strokes"].append(stroke)
                    stroke_number = extract_stroke_number(stroke['id'])
                    strokes.append((stroke_number, stroke['d']))
                    # Add this stroke to its the radical stroke lists where needed
                    radicals = current_attribs.get(radical_attrib, {})
                    for radical in radicals:
                        self.radical_strokes[radical].append(stroke_number - 1)  # 1 -> 0 based index
                    continue

                if element.tag == group_tag:
                    # Start a new kanji stroke group
                    group = dict(element.items())
                    _g = self.__class__.StrokeGroup.from_element(element)  # just a test, will replace "group = dict(element.items())"
                    # deleted by GPT
                    current_radicals = current_attribs.get(radical_attrib, set())
                    new_radical = group.get(radical_attrib, "")
                    if current_radicals or new_radical:
                        group[radical_attrib] = copy.copy(current_radicals)
                        assert isinstance(group[radical_attrib], set)
                        if new_radical:
                            cast(set, group[radical_attrib]).update({
                                radical_name.strip()
                                for radical_name in new_radical.split(",")
                            })
                    # end deleted by GPT
                    group["strokes"] = []  # type: ignore
                    group["groups"] = []  # type: ignore
                    queue.append((element, group))  # Add subgroup to queue
                    current_attribs["groups"].append(group)
                    continue

                logger.warning("tag '%s' ignored processing groups", element.tag)

            # for debug auditing purposes. Review: Do I really need different sets?
            completed_attribs.add(id(current_attribs))
            completed_groups.add(id(current_group))

        return [s for (_, s) in sorted(strokes)]

    def _load_all_labels(self, labels_group: ET.Element, _labels: list[tuple[Transform, str]]):
        """
        Extract a mapping from stroke numbers to stroke labels.

        :return: None

        .. only:: dev_notes

            - deal with the hack converting the matrix xforms into plain translates.  Experimenting.
            - consider a parser on the Transform class

        """
        for text in labels_group.findall("svg:text", self.namespace):
            assert text is not None, "Unexpected 'text is None'"
            assert isinstance(text, ET.Element), f"Unexpected text type '{type(text)}' found in the svg."
            assert "transform" in text.attrib, "Missing 'transform' attribute on the stroke text."
            position = text.attrib['transform']
            assert position[:7] == "matrix(" and position[-1] == ")", "Expected text positions to be matrix transforms"
            position_xform = Transform()  # put a parser on the Transform class?
            matrix = list(map(float, position[7:-1].split()))
            assert len(matrix) == 6, "A valid matrix must have 6 elements."
            if matrix[:4] == [1.0, 0.0, 0.0, 1.0]:
                position_xform.translate(*matrix[-2:])
            else:
                position_xform.matrix(*matrix)
            assert isinstance(text.text, str), "OMFG the type linter is SOOOOO whiny!"
            self._labels.append((position_xform, text.text))

    def load(self) -> None:
        """
        Parse KanjiVG XML for stroke paths and order.

        The SVG strokes are are stored in "/path/to/svg/<kanji codepoint in hex>.svg".

        This method is a mutator:  we'll store the list of stroke paths on the instance.

        :return: None

        :raises ValueError: for an incomplete or syntactically invalid kanji SVG

        .. only:: dev_notes

            - Thread safety: we have instance mutators!  Probably should protect this with a lock of some kind.
            - ideally _load_all_groups shouldn't have any mutating side effects

        """
        if self.loaded:
            return

        kanji_unicode = f"{ord(self.glyph):05x}"  # Convert Kanji to Unicode hex (e.g., '66f8' for 書)
        filename = f"{settings.kanji_svg_path}/{kanji_unicode}.svg"

        # Use the XML element tree module to parse the SVG content
        tree = ET.parse(filename)
        root = tree.getroot()

        # We require a viewBox attribute for the glyph boundaries and centering.
        viewbox = root.attrib.get("viewBox", None)
        if viewbox is None:
            raise ValueError(f"No viewBox found in {filename}")
        self.min_x, self.min_y, self.width, self.height = map(float, viewbox.split())

        # Find the topmost group in the strokes then extract them from <path> elements
        strokes_group = root.find(f"svg:g[@id='kvg:{self.strokepaths_id}']", self.namespace)
        if strokes_group is None:
            raise ValueError(f"Malformed SVG:  no strokes group found in {filename}")
        topmost_group = strokes_group.find(f"svg:g[@id='kvg:{self.topmost_id}']", self.namespace)
        assert not self._strokes, "Unexpected strokes present that are about to be clobbered."
        self._strokes = self._load_all_groups(topmost_group)  # need to eliminate all the side effects of this method

        # Extract stroke order numbering from <text> elements
        self._labels: list[tuple[Transform, str]] = []
        labels_group = root.find(f"svg:g[@id='kvg:{self.labels_id}']", self.namespace)
        if labels_group is not None:
            self._load_all_labels(labels_group, self._labels)

        self.loaded = True

    @property
    def strokes(self) -> list[str]:
        """
        Provide the list of SVG paths making up a stroke.

        :return: a list of string SVG pathing commands.
        """
        return self._strokes

    @property
    def center(self) -> tuple[float, float]:
        """
        Provide the center location in a drawn Kanji.

        :return: floating point (x, y) of the center of the kanji drawing in user coordinates.
        """
        return self.min_x + (self.width / 2), self.min_y + (self.height / 2)

    @property
    def viewbox(self) -> str:
        """
        Produce an SVG viewBox property to fit the kanji drawing.

        :return: the XML string format rectangle enclosing the kanji drawing user coordinate space with origin at (0,0).
        """
        return f"0 0 {self.width} {self.height}"

    def draw_strokes(
            self,
            drawing: SVGDrawing,
            stroke_range: Iterable[int] | int | slice,
            style: dict[str, Any],
            transform: Transform | None,
            with_labels: bool = False
        ):
        """
        Draw a particular subset of strokes onto an SVG drawing instance.

        :param drawing: An SVG drawing instance.
        :param stroke_range: The stroke indices to draw
        :param style: the SVG style to apply the the strokes' paths.
        :param transform: The coordinate transform to apply for the draw operation
        :param with_labels: True when we should labels the strokes as well as drawing them.

        :return: None
        """
        # hacksville
        strokes = []
        match stroke_range:
            case stroke_list if isinstance(stroke_list, (list, set)):
                strokes = [self._strokes[i] for i in stroke_list]
                labels = [self._labels[i] for i in stroke_list]
            case stroke_index if isinstance(stroke_index, int):
                strokes = [self._strokes[stroke_index]]
                labels = [self._labels[stroke_index]]
                stroke_range = slice(stroke_index, stroke_index+1, 1)
            case stroke_slice if isinstance(stroke_range, slice):
                strokes = self._strokes[cast(slice, stroke_slice)]
                labels = self._labels[cast(slice, stroke_slice)]
            case _:  # pragma: no cover
                raise ValueError("Unknown stroke range type.")  # pragma: no cover

        for stroke in strokes:
            if transform:
                drawing.add(drawing.path(d=stroke, transform=f"{transform}", **style))
            else:
                drawing.add(drawing.path(d=stroke, **style))

        if with_labels:
            for label in labels:
                assert len(label) == 2
                position_xform, stroke_label = label[0], label[1]
                drawing.add(drawing.text(stroke_label, transform=f"{transform} {position_xform}", insert=(0.0, 0.0), **self.label_style))

    def draw_glyph(
            self,
            *,
            radical: str | None = None,
            radical_only: bool = False,
            no_center: bool = False,
            image_size: Extent = DFLT_GLYPH_SIZE
        ) -> SVGDrawing:
        """
        Create an inline SVG representation of a Kanji stroke ordering.

        :param radical: which radical stroke set (if any) to highlight.
        :param radical_only: only draw the strokes in the selected radical when True
        :param no_center: suppress centering the glyph drawing in the bounding rectangle when True
        :param image_size: the size of the resulting drawing in real-world physical coordinates.
            This is required to set the scaling in the returned SVG drawing.

        :return: A complete well-formed SVG drawing instance containing the stroked kanji (or kana) glyph ready to be rendered by the client

        .. only:: dev_notes

            - can I lift the requirement to pass in image_size?  It makes this function a little clumsy.
            - can I replace self.loaded with a computed parameter inferred from the rest of the state?

        """
        assert self.loaded, "Unexpected call to draw_glyph"  #: remove self.loaded in favor of better logic

        # The user coordinate size of the image is exactly the viewbox size + the size of a stroke label on each side
        # This has __nothing__ to do with the passed image size - that's consumed by SVG in the viewBox -> size mapping.
        font_size = Distance.parse(self.label_style['font_size'])
        per_char_x = self.width + 2*int(font_size.px)  # pylint: disable=no-member
        per_char_y = self.height + 2*int(font_size.px)  # pylint: disable=no-member

        drawing = self.drawing_factory(
            size=(str(image_size.width), str(image_size.height)),  # <-- this measurement in the real world
            viewBox=f"0 0 {per_char_x} {per_char_y}"  # <-- corresponds to these user unit dimensions the drawing world
        )

        # Compute the centering transform.  Use an identity transform if we're not centering.
        char_center_x, char_center_y = self.center
        centering_transform = Transform()
        if not no_center:
            centering_transform.translate((per_char_x//2 - char_center_x), (per_char_y//2 - char_center_y))
        else:
            centering_transform = None

        net_transform = centering_transform

        # Pick out the strokes in the radical & strokes not in the radical - then draw what we've been asked to draw
        in_radical = set() if (radical is None or radical not in self.radical_strokes) else self.radical_strokes[radical]
        not_in_radical = set(range(len(self.strokes))).difference(in_radical)
        if not radical_only:
            self.draw_strokes(drawing, not_in_radical, self.stroke_styles["completed"], net_transform)
        if in_radical:
            self.draw_strokes(drawing, in_radical, self.stroke_styles["radical"], net_transform)

        return drawing

    def compute_layout(
            self,
            cell_width: Distance,
            cell_count: int,
            cell_height: Distance | None = None
        ) -> tuple[tuple, tuple, tuple[str, str], Transform]:
        """
        Compute the drawing layout metrics for a kanji stroke steps diagram.

        :param cell_width: the amount of horizontal space allocated for drawing the glyph.
        :param cell count: the number of full or partial glyphs to draw.
        :param cell_height: the amount of vertical space allocated for drawing the glyph, defaults to <cell_width>.

        :return: tuple of

            - cell_size - (width, height) of each stoke step cell in user units
            - image_size - (width, height) of the entire stoke diagram in user units
            - image_size_str - image_size as an SVG attribute string in whatever units cell_width/height came with
            - centering_transform - matrix transform that puts each stroke step in the center of its cell
        """
        cell_extent = Extent(cell_width, cell_width if cell_height is None else cell_height)
        cell_size = (cell_extent.width.user, cell_extent.height.user)
        image_width = cell_count*cell_extent.width
        image_height = cell_extent.height
        image_size = (str(image_width), str(image_height))

        char_center_x, char_center_y = self.center
        centering_transform = Transform()
        centering_transform.translate((cell_extent.width.user//2 - char_center_x), (cell_extent.height.user//2 - char_center_y))

        return (cell_size, (image_width.user, image_height.user), image_size, centering_transform)

    def draw_practice_axes(self, drawing: SVGDrawing, cell_count: tuple[int, int], cell_px_width: int, cell_px_height: int) -> None:
        """
        Draw practice guidelines in each kanji stroke step cell

        :param drawing: the SVG drawing instance that will receive the guidelines
        :param cell_count: the total number of kanji stroke step cells
        :param cell_width: width of each cell
        :param cell_height: (optional) - height of each cell, defaults to the width

        :return: None

        .. only:: dev_notes

            - can I do better drawing the diagonal practice lines?  the current loop is inefficient.  (Does that inefficiency matter?)

        """
        cells_wide, cells_tall = cell_count
        image_px_width = cells_wide*cell_px_width

        # vertical practice lines
        logger.info("Drawing vertical practice lines")
        delta = cell_px_width/2
        for i in range(1, 2*cells_wide, 2):
            top, bottom = (i*delta, 0), (i*delta, cells_tall*cell_px_height)
            logger.info("column %s: drawing a line from %s to %s", i, top, bottom)
            drawing.add(drawing.line(start=top, end=bottom, **self.practice_line_style))

        # horizontal practice lines
        logger.info("Drawing horizontal practice lines")
        delta = cell_px_height/2
        for j in range(1, 2*cells_tall, 2):
            left, right = (0, j*delta), (image_px_width, j*delta)
            logger.info("row %s: drawing a line from %s to %s", j, left, right)
            drawing.add(drawing.line(start=left, end=right, **self.practice_line_style))

        # Diagonal practice lines
        # Maybe candystripe instead of iterating over rows?
        logger.info("Drawing diagonal practice lines")
        for (i, j) in product(range(1, cells_wide+1), range(cells_tall)):
            left_x, right_x = (i-1)*cell_px_width, i*cell_px_width
            top_y, bottom_y = j*cell_px_height, (j+1)*cell_px_height
            logger.info(
                "cell = %s: drawing a line from top left %s to bottom right %s and %s to %s",
                (i, j),
                (left_x, top_y), (right_x, bottom_y),
                (right_x, top_y), (left_x, bottom_y)
            )
            drawing.add(drawing.line(start=(left_x, top_y), end=(right_x, bottom_y), **self.practice_line_style))
            drawing.add(drawing.line(start=(right_x, top_y), end=(left_x, bottom_y), **self.practice_line_style))

    def draw_cell_dividers(self, drawing: SVGDrawing, cell_count: tuple[int, int], cell_px_width: int, cell_px_height: int) -> None:
        """
        Draw vertical divider lines between each of the kanji stroke step cells.

        :param drawing: - SVG drawing entity that receives the guidelines
        :param cell_count: the total number of kanji stroke step cells
        :param cell_width: width of each cell
        :param cell_height: (optional) - height of each cell, defaults to the width

        :return: None

        .. only:: dev_notes

            - express the image pixel size calculation as an inner product?

        """
        cells_wide, cells_tall = cell_count
        image_px_size = (cells_wide*cell_px_width, cells_tall*cell_px_height)  # call out to an inner product function?

        # image frame
        logger.info("Drawing the image frame rectangle")
        logger.info("drawing a rect at %s size=%s", (0, 0), image_px_size)
        drawing.add(drawing.rect(insert=(0, 0), size=image_px_size, **self.cell_border_style))

        # vertical cell dividers
        logger.info("Drawing the vertical separators")
        for i in range(1, cells_wide):
            logger.info("column %s: drawing a line from %s to %s", i, (i*cell_px_width, 0), (i*cell_px_width, cells_tall*cell_px_height))
            drawing.add(drawing.line(
                start=(i*cell_px_width, 0),
                end=(i*cell_px_width, cells_tall*cell_px_height),
                **self.cell_border_style
            ))

        # horizontal cell dividers
        logger.info("Drawing the horizontal separators")
        for j in range(1, cells_tall):
            logger.info("row %s: drawing a line from %s to %s", j, (0, j*cell_px_height), (cells_wide*cell_px_width, j*cell_px_height))
            drawing.add(drawing.line(
                start=(0, j*cell_px_height),
                end=(cells_wide*cell_px_width, j*cell_px_height),
                **self.cell_border_style
            ))

    def draw_stroke_steps(self, grid_columns: int, cell_size: Extent = DFLT_GLYPH_SIZE) -> SVGDrawing:
        """
        Create an inline SVG representation of a Kanji stroke ordering.

        :param grid_columns: the maximum number of stroke steps to draw before starting a new row of step cells.
        :param cell_size: the size of the drawn cell in real-world physical coordinates.
            This is required to set the scaling in the returned SVG drawing.

        :return: A complete well-formed SVG drawing instance containing a step-by-step diagram for stroking the kanji (or kana) glyph,
            ready to be rendered by the client.

        .. only:: dev_notes

            - can I lift the requirement to pass in image_size?  It makes this function a little clumsy.
            - can I replace self.loaded with a computed parameter inferred from the rest of the state?
            - should the KanjiSVG have more spacing options baked into the instance: inter-step margins, top/bottom margins?

        """

        assert self.loaded, "unexpected call to draw_stroke_steps"

        # We're going to draw the entire character first then 1 cell per stroke
        # So the total image width is (#strokes + 1)*cell width
        #
        stroke_count = len(self._strokes)
        grid_rows = (stroke_count // (grid_columns-1)) + int(stroke_count % ((grid_columns-1)) > 0)

        # The user coordinate size of the image is exactly the viewbox size + the size of a stroke label on each side
        # This has __nothing__ to do with the passed image size - that's consumed by SVG in the viewBox -> size mapping.
        #  With this tactic, I will need to pass in inter-step and top/bottom spacing as options
        font_size = Distance.parse(self.label_style['font_size'])
        per_char_x = self.width + 2*font_size.px  # pylint: disable=no-member
        per_char_y = self.height + 2*font_size.px  # pylint: disable=no-member

        # image_size = Extent((stroke_count + 1)*cell_size.width, cell_size.height)
        image_size = Extent(grid_columns*cell_size.width, grid_rows*cell_size.height)
        drawing = self.drawing_factory(
            size=(str(image_size.width), str(image_size.height)),  # <-- this measurement in the real world corresponds to these...
            viewBox=f"0 0 {int(per_char_x*grid_columns + 1.0)} {int(per_char_y*grid_rows + 1.0)}"  # ...user unit measures the drawing world
        )

        # Position each partial glyph in cell with a sliding window coordinate transform
        char_center_x, char_center_y = self.center
        centering_transform = Transform()
        centering_transform.translate((per_char_x//2 - char_center_x), (per_char_y//2 - char_center_y))
        line_start = centering_transform
        line_cell_window = copy.copy(line_start)  # DO NOT FORGET TO COPY!

        # The meat of the matter.  Draw everybody - note the use of translations to slide the cell window in the for-loop
        self.draw_practice_axes(drawing, (grid_columns, grid_rows), per_char_x, per_char_y)
        self.draw_cell_dividers(drawing, (grid_columns, grid_rows), per_char_x, per_char_y)
        self.draw_strokes(drawing, slice(0, len(self.strokes)), self.stroke_styles["completed"], line_cell_window)
        for stroke_number in range(stroke_count):
            logging.info("Drawing stroke #%s", stroke_number)
            line_cell_window.translate(per_char_x, 0)
            self.draw_strokes(drawing, slice(0, stroke_number), self.stroke_styles["completed"], line_cell_window)
            self.draw_strokes(drawing, stroke_number, self.stroke_styles["next"], line_cell_window, with_labels=True)
            if (stroke_number + 1) % (grid_columns - 1) == 0:
                logging.info("Moving to a new line after stroke #%s", stroke_number)
                line_start.translate(0, per_char_y)
                line_cell_window = copy.copy(line_start)
        return drawing

    def draw_practice_strip(self, grid_columns: int, cell_size: Extent = DFLT_GLYPH_SIZE) -> SVGDrawing:
        """
        Create an inline SVG representation of a strip of practice cells.

        :param grid_columns: the maximum number of stroke steps to draw before starting a new row of step cells.
        :param cell_size: the size of each practice cell in real-world physical coordinates.
            This is required to set the scaling in the returned SVG drawing

        :return: A complete well-formed SVG drawing instance containing a the kanji on the left and empty cells to the right for practice,
            ready to be rendered by the client.

        .. only:: dev_notes

            - can I lift the requirement to pass in image_size?  It makes this function a little clumsy.
            - can I replace self.loaded with a computed parameter inferred from the rest of the state?
            - should the KanjiSVG have more spacing options baked into the instance: inter-step margins, top/bottom margins?

        """
        assert self.loaded, "unexpected call to draw_practice_strip"

        # We're going to draw the entire character first then 1 cell per stroke
        # So the total image width is (#strokes + 1)*cell width
        #
        grid_rows = 1

        # The user coordinate size of the image is exactly the viewbox size + the size of a stroke label on each side
        # This has __nothing__ to do with the passed image size - that's consumed by SVG in the viewBox -> size mapping.
        # With this tactic, I will need to pass in inter-step and top/bottom spacing as options
        font_size = Distance.parse(self.label_style['font_size'])
        per_char_x = self.width + 2*font_size.px  # pylint: disable=no-member
        per_char_y = self.height + 2*font_size.px  # pylint: disable=no-member

        # image_size = Extent((stroke_count + 1)*cell_size.width, cell_size.height)
        image_size = Extent(grid_columns*cell_size.width, grid_rows*cell_size.height)
        drawing = self.drawing_factory(
            size=(str(image_size.width), str(image_size.height)),  # <-- this measurement in the real world corresponds to these...
            viewBox=f"0 0 {int(per_char_x*grid_columns + 1.0)} {int(per_char_y*grid_rows + 1.0)}"  # ...user unit measures the drawing world
        )

        # Position each partial glyph in cell with a sliding window coordinate transform
        char_center_x, char_center_y = self.center
        centering_transform = Transform()
        centering_transform.translate((per_char_x//2 - char_center_x), (per_char_y//2 - char_center_y))
        line_start = centering_transform
        line_cell_window = copy.copy(line_start)  # DO NOT FORGET TO COPY!

        # The meat of the matter.  Draw everybody.
        self.draw_practice_axes(drawing, (grid_columns, grid_rows), per_char_x, per_char_y)
        self.draw_cell_dividers(drawing, (grid_columns, grid_rows), per_char_x, per_char_y)
        self.draw_strokes(drawing, slice(0, len(self.strokes)), self.stroke_styles["completed"], line_cell_window, with_labels=True)

        return drawing


if __name__ == '__main__':  # pragma: no cover
    with log("./kanji_svg.log", logging.DEBUG):
        inline_svg = KanjiSVG("戸").draw_stroke_steps(grid_columns=6)
        display(SVG(data=inline_svg))

        logger.info(chr(int("f9ab", 16)))
        inline_svg = KanjiSVG(chr(int("f9ab", 16))).draw_glyph(radical="general")
        display(SVG(data=inline_svg))
        inline_svg = KanjiSVG(chr(int("f9ab", 16))).draw_stroke_steps(grid_columns=6)
        display(SVG(data=inline_svg))

        logger.info(chr(int("04e94", 16)))
        inline_svg = KanjiSVG(chr(int("04e94", 16))).draw_glyph(radical="tradit")
        display(SVG(data=inline_svg))
        inline_svg = (k := KanjiSVG(chr(int("04e94", 16)))).draw_stroke_steps(grid_columns=6)
        logger.info(k.radical_strokes)
        display(SVG(data=inline_svg))
