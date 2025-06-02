"""
Define geometry primitives for layout modeling.

Layout in Kanji Time operates in a unit-aware 2D coordinate space, using value types to express physical dimensions, screen-relative
distances, and nested layout regions.

All elements are grounded in a shared system of immutable types:

  - `Distance` - scalar lengths with precise units and soft constraint logic
  - `Pos` - 2D points used for frame origins and anchor positions
  - `Extent` - dimensions (width, height) used for sizing and layout negotiation
  - `Region` - rectangular areas used to scope layout frames
  - `AnchorPoint` - symbolic compass-style alignment hints

These types support arithmetic, layout rules, and diagnostics.
They are passed between `ContentFrame` objects during layout and render phases and provide the backbone for all geometry-aware layout
strategies.

Each class is derived from `namedtuple`, but extended with layout-specific operations like addition, anchoring, intersection, and scaling.

Class Relationships
-------------------

These classes have a small dependency footprint.  They model spatial abstraction enhancements building up from the Distance type.

.. mermaid::
    :name: cd_geometry
    :caption: Class relationships for the geometry model.

    ---
    config:
        mermaid_include_elk: "0.1.7"
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        note "All of Pos, Extent, and Region have  a rich set of arithmetic methods beyond what is shown here."
        class namedtuple
        namedtuple <|-- Pos
        namedtuple <|-- Extent
        namedtuple <|-- Region
        class Distance {
            <<immutable>>
        }

        class Pos {
            <<immutable>>
            +x : Distance
            +y : Distance
            +__add__(Pos) : Pos
            +__neg__() : Pos
        }

        class Extent {
            <<immutable>>
            +width : Distance
            +height : Distance
            +__add__(Extent) : Extent
            +__sub__(Extent) : Extent
            +anchor_at(anchor, Extent) : Pos
            +coalesce(other) : Extent
        }

        class Region {
            <<immutable>>
            +origin : Pos
            +extent : Extent
            +__contains__(other) : bool
            +bounds(unit) : tuple
        }

        Region --> Pos : origin
        Region --> Extent : extent
        Extent --> Distance : width, height
        Pos --> Distance : x, y

----

.. seealso:: :doc:`dev_notes/region_notes`

----

"""
# pylint: disable=fixme,no-self-argument

from collections import namedtuple
from collections.abc import Callable
from fractions import Fraction
from typing import Any, Self
from copy import copy

from kanji_time.utilities.class_property import classproperty
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.anchor_point import AnchorPoint

# pylint: disable=wrong-import-position, wrong-import-order
import logging
logger = logging.getLogger(__name__)


ExtentTuple = namedtuple('Extent', "width height")
PosTuple = namedtuple('Pos', "x y")
RegionTuple = namedtuple("Region", "origin extent")


class Pos(PosTuple):
    """
    Model a position in 2-space as an ordered pair of distances.

    .. only:: dev_notes

        - I could model a coordinate system's axis conventions by providing combiners for underlying binops.

    """
    @classproperty
    def zero(cls) -> Self:
        """Produce a new known position at (0, 0)."""
        return Pos(Distance.zero, Distance.zero)  # type: ignore

    def __str__(self):
        """Produce a human-readable representation."""
        s = tuple(map(str, self))
        return f"x={s[0]}, y={s[1]}"

    def __repr__(self):
        """Produce a reconstruction representation."""
        r = tuple(map(repr, self))
        return f"{self.__class__.__name__}({r[0]}, {r[1]})"

    def __neg__(self):
        """Produce new position reflected through (0, 0)."""
        return Pos(-self.x, -self.y)

    def __add__(self, other):
        """Produce a new position that treats other as a delta adding its (possibly signed) x &  y to my own."""
        match other:
            case Pos(x, y):
                return Pos(self.x + x, self.y + y)
        raise ValueError(f"addition not defined for Pos and {type(other)}")

    def logstr(self):
        """Produce a debugging string representation for the logs."""
        return f"position (x={self.x.logstr()}, y={self.y.logstr()})"


class Extent(ExtentTuple):
    """Model a rectangular extent as an ordered pair of distances."""

    def coalesce(self, other):
        """Construct a new Extent instance with zero values in <self> filled in from <other>."""
        return Extent(self.width or other.width, self.height or other.height)

    def anchor_at(self, anchor_pt, other: 'Extent') -> Pos:
        """
        Position myself inside the <other> extent according the anchor point rules.

        Where do I position myself inside other with the anchor?
        Assuming PDF coordinate system.
        """
        my_center = Pos(self.width // 2, self.height //2)
        other_center = Pos(other.width // 2, other.height //2)

        # Position my left side
        if AnchorPoint.W in anchor_pt:
            x = Distance.zero
        elif AnchorPoint.E in anchor_pt:
            x = other.width - self.width
        else:
            x = other_center.x - my_center.x

        # Position my right side
        if AnchorPoint.S in anchor_pt:
            y = Distance.zero
        elif AnchorPoint.N in anchor_pt:
            y = other.height - self.height
        else:
            y = other_center.y - my_center.y

        return Pos(x, y)

    def conditional_replace(self, condition: Callable[[Any, Any], bool], **kwargs):
        """
        Create a new instance replacing fields with the passed keyword args whose old/new values satisfy the <condition> predicate.

        ..only:: dev_notes

            - Factor: extract this method to a `namedtuple_goodies` add-in.
        """
        filtered_kwargs = {
            key: value
            for key, value in kwargs.items()
            if condition(value, getattr(self, key))
        }
        if filtered_kwargs:
            return self._replace(**filtered_kwargs)
        return self

    def __str__(self):
        """Produce a human readable representation."""
        s = tuple(map(str, self))
        return f"width={s[0]}, height={s[1]}"

    def __repr__(self):
        """Produce a reconstruction representation."""
        r = tuple(map(repr, self))
        return f"{self.__class__.__name__}({r[0]}, {r[1]})"

    def __bool__(self):
        """Produce True when non-empty."""
        # An extent must have both width and height be non-empty.
        return bool(self.width) and bool(self.height)

    def __contains__(self, other: object) -> bool:
        """Produce True when <other> is weakly inside myself assuming a common origin."""
        match other:
            case Extent(w, h):
                return w <= self.width and h <= self.height
            case Pos(x, y):
                return x <= self.width and y <= self.height
        raise ValueError(f"Cannot test {other} for containment in {self}")

    def __add__(self, other):
        """Produce a new extent that adds <other>'s width and height to my own."""
        match other:
            case Extent(width, height):
                return Extent(self.width + width, self.height + height)
        raise ValueError(f"addition not defined for Extent and {type(other)}")

    def __sub__(self, other):
        """Produce a new extent that reduces my own width and height by <other>'s, with a min of zero."""
        match other:
            case Extent(width, height):
                if self.width < width or self.height < height:
                    logging.warning(
                        "Subtracting a larger extent from a smaller:  %s - %s. Clamping offending dimensions to 0",
                        self, other
                    )
                return Extent(max(self.width - width, Distance.zero), max(self.height - height, Distance.zero))
        raise ValueError(f"subtraction not defined for Extent and {type(other)}")

    def __mul__(self, other: object):
        """Produce a new extent that scales my width and height by a factor of <other>."""
        return Extent(other*self.width, other*self.height)

    def __rmul__(self, other: object):
        """Produce a new extent that scales my width and height by a factor of <other>."""
        return Extent(self.width*other,self.height*other)

    # def __imul__(self, other: object):
    #     # NOPE - tuples are immutable.  But nice try
    #     self.width *= other
    #     self.height *= other
    #     return self

    def __floordiv__(self, other):
        """Produce a new extent that reduces my width and height by a factor of <other>."""
        # I can floordiv by another extent to produce a pure number - same story on truediv
        if not isinstance(other, (Fraction, int)):
            raise ValueError("Cannot divide an extent by a non-scalar.")
        return Extent(self.width // other, self.height // other)

    def __truediv__(self, other):
        """Produce a new extent that reduces my width and height by a factor of <other>."""
        if not isinstance(other, (float, Fraction, int)):
            raise ValueError("Cannot divide an extent by a non0-scalar.")
        return Extent(self.width / other, self.height / other)

    # def __isub__(self, other):
    #     match other:
    #         case Extent(w, h):
    #             self.width -= w
    #             self.height -= h
    #             return self
    #     raise ValueError(f"isub not available for type {type(other)}")

    def __or__(self, other):
        """Produce a new extent that has the larger width and height (each) of my own and <other>'s ."""
        if other is None:
            return copy(self)
        match other:
            case Extent(width, height):
                return Extent(max(self.width, width), max(self.height, height))
        raise ValueError(f"Extent.union is not available for type {type(other)}")

    def __and__(self, other):
        """Produce a new extent that has the smaller width and height (each) of my own and <other>'s ."""
        if other is None:
            return Extent.zero
        match other:
            case Extent(width, height):
                return Extent(min(self.width, width), min(self.height, height))
        raise ValueError(f"Extent.intersect is not available for type {type(other)}")

    def logstr(self):
        """Produce a debugging string representation for the logs."""
        return f"extent {' by '.join(map(Distance.logstr, (self.width, self.height)))}"

    @classproperty
    def fit_to(cls) -> Self:
        """Produce a new known extent that models being fit into some unknown constraints."""
        return Extent(Distance.fit_to, Distance.fit_to)  # type: ignore

    @classproperty
    def zero(cls) -> Self:
        """Produce a new known empty extent."""
        return Extent(Distance.zero, Distance.zero)  # type: ignore


class Region(RegionTuple):
    """
    Model a local coordinate system of size <extent> that is offset by <origin> from some larger Region's origin.

    .. only:: dev_notes

        - I could model a coordinate system's axis conventions by providing combiners for underlying binops.

    """

    def __contains__(self, other: object) -> bool:
        """
        Produce True when <other> is weakly inside myself.

        Operates on other regions, plain extents, and positions.

        .. only:: dev_notes

            - *** Works in absolute coordinates. *** <-- is this really true?
            - there are axis direction issues all over this.  Derive from an coordinate system object?

        """
        match other:
            case Region(o, e):
                # We contain the origin and the opposite corner
                return o in self and Pos(o.x + e.width, o.y + e.height) in self
            case Extent(w, h):
                return Extent(w, h) in self.extent
            case Pos(x, y):
                return Pos(x - self.origin.x, y - self.origin.y) in self.extent
        raise TypeError(f"containment not defined for Region and {type(other)}")

    def bounds(self, unit):
        """
        Produce unitless tuples for the origin & extent converted to <unit>.

        This is useful for passing regions down to third party functions that operate on
        known units using plain numbers - floats, ints, et al.

        .. only:: dev_notes

            - another instance of coordinate vector orientation assumptions.
              coordinate mapping, left- or right-relative and top- or bottom- relative
            - bounds is intended to feed a rendering technology so getting the axis directions
              right is critical -- this is tuned to ReportLab conventions.

        """
        convert = lambda d: d.to(unit).measure
        return (tuple(map(convert, self.origin)), tuple(map(convert, self.extent)))

    def __str__(self):
        """Produce a human readable representation."""
        s = tuple(map(str, self.bounds("in")))
        return f"origin={s[0]}, extent={s[1]}"

    def __repr__(self) -> str:
        """Produce a reconstruction representation."""
        return f"{self.__class__.__name__}({self.origin!r}, {self.extent!r})"

    def __add__(self, other):
        """
        Produce a new region offset from myself by <other>.

        * NOTE *
            It's an abuse of notation to take a Pos instance as the delta,
            but that is the most convenient way to change coordinate systems in nested
            regions.  I don't want to create a delta type out of a misguided sense of
            purity.
        """
        match other:
            case Pos(_, _):
                return Region(self.origin + other, self.extent)
        raise ValueError(f"addition not defined for Pos and {type(other)}")

    def logstr(self):
        """Produce a debugging string representation for the logs."""
        return f"region @ {self.origin.logstr()}, {self.extent.logstr()}"
