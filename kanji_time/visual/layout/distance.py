"""
Define an immutable distance type for regions for layout.

Distance is the foundational unit of measurement in the layout system. It models real-world dimensions
(e.g., inches, points, millimeters) and supports precise arithmetic using rational math internally.

It also supports soft layout constraints via symbolic forms:

- '*' for fit-to-space behavior (e.g., '5in*' is "at least 5 inches")
- '!' for infinite/overflow behavior
- '%' and user units for device-relative or font-relative rendering

Conversions to specific units are seamless via attribute access such as `distance.inch` or `distance.pt`, among others.

All Distance math preserves rational precision unless explicitly cast to float. In layout engines like
StackLayout or Page, Distance provides the canonical language for measuring, positioning, and allocating
rendered content.

Class Relationships
-------------------

As a foundational utility type, the Distance class has a very small dependency surface.

.. mermaid::
    :name: cd_geometry_distance
    :caption: Class structure of a distance measurement.

    ---
    config:
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        class Distance {
            <<immutable>>
            +to(unit: DistanceUnit) Distance
            +inch : float
            +pt : float
            +fix_to(other: Distance) Distance
            +\_\_add\_\_(other) Distance
        }
        Distance ..> DistanceUnit : the units for the enclosed distance measure
        Distance ..> Fraction : used for exact measure arithmetic
        note for Distance "__add__ is representative. There is a rich set of robust arithmetic operations for manipulating Distance instances."

----

.. seealso:: :doc:`dev_notes/distance_notes`

----

"""

# pylint: disable=fixme, no-self-argument

from collections import namedtuple
from collections.abc import Callable
from fractions import Fraction
import math

from copy import copy

import enum
import re
from typing import ClassVar

from kanji_time.utilities.class_property import classproperty


class DistanceUnit(enum.StrEnum):
    """Define measurement units for distance."""
    # review enum.StrEnum semantics I think I'm duplicating work in this module when using DistanceUnit.
    # pylint: disable=invalid-name
    em = "em"
    ex = "ex"
    px = "px"
    pt = "pt"
    pc = "pc"
    cm = "cm"
    mm = "mm"
    inch = "in"
    pct = "%"
    rest = "*"
    infinite = "!"
    user = "u"  # SVG user units @ 1/96th inch


unit_str = {
    str(u): u for u in DistanceUnit
}


# see SO:  https://stackoverflow.com/a/606307
# 1 pica = 1/72 inch
# IRL, 996 points are equivalent to 35 centimeters, so a point is 10/723 inches --> 1/72 inch
# 1 pica point is  1/12 pica
twips_factor = {
    DistanceUnit.em: None,
    DistanceUnit.ex: None,
    DistanceUnit.px: 1440//96,  # same as SVG user coordinates
    DistanceUnit.pt: 20,
    DistanceUnit.pc: 1440//72,
    DistanceUnit.cm: 567,
    DistanceUnit.mm: 57,
    DistanceUnit.inch: 1440,
    DistanceUnit.pct: None,
    DistanceUnit.rest: 1,
    DistanceUnit.infinite: 1,
    DistanceUnit.user: 1440//96,
}


_Distance = namedtuple('_Distance', "measure unit at_least")


# @total_ordering
class Distance(_Distance):
    """
    Model a distance on a discrete-grained drawing surface with built-in measurement unit conversion.

    .. only:: dev_notes

        - enhance the distance constraint model for `RenderingFrame.measure` and `RenderingFrame.do_layout` methods.

            - maybe move away from fixed flags and define a distinct `Constraint` type?
            - this gets to an "apply constraints" semantic that adjusts a distance or a "satisfies constraints" that checks.
            - raises the possibility of constraint expressions linked with logical connectives.
            - who owns a constraint?  Maybe it should be decoupled from the `Distance` type.

        - the minimum constraint case is going to be at_least, at_most, and between
        - there's no implementation of "percent" units.  Percent of what?  Tie this feature to the property delegation model.
        - convert this class to a Generic parameterized by MeasureType?
        - can fit_to, zero, and infinite be expressed as Singletons?

    """
    # Factor: MeasureType needs to support ConvertibleToFloat if it doesn't already - do this later.
    MeasureType: ClassVar[type] = type(Fraction)
    __match_args__ = ("measure", "unit", "at_least")

    # fit_to, zero, and infinite should be Singletons so I can use "is" with them.
    @classproperty
    def fit_to(cls):
        """Produce a known distance that models being fit into some unknown constraints."""
        return Distance.parse("*")

    @classproperty
    def zero(cls) -> 'Distance':
        """Produce a known distance of nothing."""
        return Distance.parse("0pt")

    @classproperty
    def infinite(cls) -> 'Distance':
        """Produce a known distance that larger than any other distance except itself."""
        return Distance.parse("!")

    def __new__(cls, measure: Fraction | float, unit: str | DistanceUnit, at_least: bool = False):
        """Perform extra initialization beyond the default dataclass generated __init__ method's."""
        assert not isinstance(measure, Distance), "Distances can't nest"
        measure = Fraction(measure)
        unit = unit_str[unit] if isinstance(unit, str) else unit # Force units to be in the enumerated unit type
        return super().__new__(cls, measure, unit, at_least)

    def __bool__(self):
        """Yield true for non-zero distances."""
        return not math.isclose(float(self.measure), 0.0)

    def __float__(self):
        """Conversion to silence ConvertibleToFloat issues."""
        return float(self.measure)

    def to(self, unit: DistanceUnit):
        """Convert distance to a particular measurement unit."""
        assert isinstance(unit, str)
        if unit not in unit_str:
            raise ValueError(f"Unrecognized target unit for conversion: '{unit}'")
        if unit == self.unit:
            return copy(self)
        assert isinstance(self.unit, DistanceUnit)
        return Distance(twips_factor[self.unit]*self.measure/twips_factor[unit], unit, self.at_least)

    def __str__(self) -> str:
        """
        Render the distance as a user friendly string with the current units.

        .. only:: dev_notes

            - Provide a settable # of significant digits - or even a preferred string format

        """
        return f"{'>=' if self.at_least else ''}{round(float(self.measure), 1)}{unit_str[self.unit]}"

    def __repr__(self) -> str:
        """Produce a reconstruction representation."""
        return f"{self.__class__.__name__}({self.measure}, '{str(self.unit)}', at_least={self.at_least})"

    def __copy__(self) -> 'Distance':
        """A copy of this instance."""
        return Distance(self.measure, self.unit, self.at_least)

    @classmethod
    def parse(cls, d: str, at_least: bool = False):
        r"""Parse a number in the form \d+([.]\d*)?)([^\d]{1,2}) + a unit suffix into a distance"""
        if not d:
            raise ValueError("Must pass a non-empty string.")
        if d[-1] in '*!':
            if len(d) == 1:
                unit = d[-1]
                return Distance(Fraction(0), unit) # , at_least=True)
            # allow "5in*" for a stretchy measure that needs to be at least 5 inches.
            d = d[:-1]
            at_least = True

        dist_re = re.compile(r"(\d+([.]\d*)?)([^\d]{1,2})")  # Review:  pull out the magic regexp to a property
        m = dist_re.fullmatch(d)
        if not m:
            raise ValueError(f"'{d}' is not a distance measurement.")
        if m[3] not in unit_str:
            raise ValueError(f"'{m[3]}' is not a distance unit.")
        return Distance(Fraction(m[1]), m[3], at_least)

    # ISSUE: For arithmetic, consider converting to the finer grained unit (or even both to twips)
    #        do the operation, then convert to the result unit.
    #        --> would it be better to always express Distance.measure in the finest grained unit available? 1/10th of that?

    @classmethod
    def __zero__(cls):  # for sum()
        """Additive identity."""
        return cls.zero

    def fix_to(self, other):
        """Fix a variable distance to a particular value if it satisfies the distance criterion."""
        if other.unit == "*":  # or other.at_least
            raise ValueError("May only fix a distance to a fixed distance.")
        if self.unit != "*" and not self.at_least:
            return copy(self)
        if self.at_least and other < self:
            raise ValueError("Fixing a distance to too small of a value.")
        if self.unit != '*':
            return other.to(self.unit)
        return copy(other)

    def __neg__(self):
        """Produce a new distance that is the additive inverse of myself."""
        if self.unit == "!":
            return self.infinite
        return Distance(-self.measure, self.unit, self.at_least)

    def __add__(self, other):
        """Sum two distances retaining the unit of this one."""
        match other:
            case Distance(measure, unit, at_least):
                if unit == '!':
                    return self.infinite
                if unit == '*':
                    return Distance(self.measure, self.unit, at_least=True)
                if self.unit == '*':
                    return Distance(measure, unit, at_least=True)
                if unit != self.unit:
                    other = other.to(self.unit)
                return Distance(self.measure + other.measure, self.unit, self.at_least or at_least)
            case int(z) if z == 0:
                return copy(self)
        raise ValueError(f"Add not supported between Distance and {type(other)} of {other}.")

    def __radd__(self, other):
        """
        Sum two distances retaining the unit of the other one.

        Addition commutes, defer to __add__ on other to keep its units.
        For adding non-distances, defer to __add__ on self.
        """
        if isinstance(other, Distance):
            return other.__add__(self)  # pragma: no cover
        return self.__add__(other)

    def __sub__(self, other):
        """Subtract two distances retaining the unit of this one."""
        return self.__add__(-other)

    def __rsub__(self, other):
        """Subtract two distances retaining the unit of that one."""
        return -self.__radd__(-other)

    # ----> DO NOT ADD __mul__ OR __div__ UNLESS IT'S ONLY BY A SCALAR:  these binops change units to areas or rates!

    def __floordiv__(self, other):
        """
        Divide a distance by a scalar.

        Dividing two unit-tagged numbers for the same dimension is possible!
        It yields a vanilla non-unit-tagged number ratio.
        """
        match other:
            case Distance(measure, unit, _):
                if unit == DistanceUnit.infinite:
                    return Distance.zero
                if measure == Distance.zero.measure:  # pylint: disable=no-member
                    raise ZeroDivisionError("Cannot divide a distance by a zero distance.")
                if DistanceUnit.rest not in {unit, self.unit}:
                    me = twips_factor[self.unit]*self.measure
                    you = twips_factor[unit]*measure
                    return me // you
                raise ValueError(f"cannot floordiv {self} with {other}")
            case 0 | 0.0:
                raise ZeroDivisionError("Cannot divide a distance by zero.")
            case int(n):
                # OOOF!  This is a real bug!  Fix it!! too late now, and it doesn't affect me immediately.  
                # floordiv & mod are a function of unit!  need to store the measure in twips and carry a truncate flag?  Ugly!
                # honestly?  I probably should not be floordiving in the first place.
                new_measure = Fraction(((twips_factor[self.unit]*self.measure / n)/twips_factor[self.unit]))
                return self._replace(measure=new_measure)

        raise ValueError(f"cannot floordiv {self} with {other}")


    def __mod__(self, other):
        """
        Modulo a distance by a scalar.

        Dividing two unit-tagged numbers for the same dimension is possible!
        It yields a vanilla non-unit-tagged number ratio.

        My result is the remaining distance after the division operation.
        """
        match other:
            case Distance(measure, unit, _):
                if unit == DistanceUnit.infinite:
                    return Distance.zero
                if measure == Distance.zero.measure:  # pylint: disable=no-member
                    raise ZeroDivisionError("Cannot divide a distance by a zero distance.")
                if DistanceUnit.rest not in {unit, self.unit}:
                    me = twips_factor[self.unit]*self.measure
                    other = twips_factor[unit]*measure
                    return self._replace(measure=(me % other)/twips_factor[self.unit])
                raise ValueError(f"cannot modulo {self} with {other}")
            case 0 | 0.0:
                raise ZeroDivisionError("Cannot divide a distance by zero.")
            case int(n):
                return self._replace(measure=self.measure%n)

        raise ValueError(f"cannot modulo {self} with {other}")

    def __truediv__(self, other):
        """Divide a distance by a scalar."""
        match other:
            case Distance(measure, unit, _):
                if unit == DistanceUnit.infinite:
                    return Distance.zero
                if measure == Distance.zero.measure:  # pylint: disable=no-member
                    raise ZeroDivisionError("Cannot divide a distance by a zero distance.")
                if DistanceUnit.rest not in (unit, self.unit):
                    me = twips_factor[self.unit]*self.measure
                    you = twips_factor[unit]*measure
                    return me / you
                raise ValueError(f"cannot truediv {self} with {other}")
            case 0 | 0.0:
                raise ZeroDivisionError("Cannot divide a distance by zero.")
            case int(x) | float(x):
                new_measure = (twips_factor[self.unit]*self.measure / x)/twips_factor[self.unit]
                return self._replace(measure=new_measure)

        raise ValueError(f"cannot truediv {self} with {other}")


    def __mul__(self, other):
        """Multiply a distance by a scalar on the right."""
        if isinstance(other, Distance):
            raise ValueError("Cannot multiply a united number by a united number - we don't have areas yet.")
        if self.unit == '!':
            return self.infinite  # pragma: no cover
        return Distance(self.measure * other, self.unit, self.at_least)

    def __rmul__(self, other):
        """Multiply a distance by a scalar on the left."""
        assert not isinstance(other, Distance), "should be in the the left multiplication for a Distance operand!"
        if self.unit == '!':
            return self.infinite  # pragma: no cover
        return self._replace(measure=other*self.measure)

    def __lt__(self, other) -> bool:
        """Compare for ordering."""
        if self.unit == '!':
            return False
        match other:
            # can I do this with Numeric semantics?  It was a PITA last time I tried it.
            case int(n) if n == 0:
                return self.measure < Fraction(n)
            case float(f) if math.isclose(f, 0.0):
                return float(self.measure) < f
            case Distance(measure, unit, _):
                if unit == '!':
                    return True
                if unit != '*' and self.unit != '*':
                    measure = other.to(self.unit).measure
                return self.measure < measure
        # Fall out to fail case
        raise ValueError(f"less than compares are undefined for types Distance and {type(other)}")

    def __ge__(self, other) -> bool:
        """Compare for ordering."""
        return not self < other

    def __eq__(self, other) -> bool:
        """
        Compare for equivalence.

        .. only:: dev_notes

            - how do constraints interact with equivalence?
              Consider for "at least 5" being equal to anything bigger than 5. This sounds like it should be a matches, not ==.

        """
        match other:
            # can I do this with Numeric semantics?  It was a PITA last time I tried it.
            case int(n) if n == 0:
                return self.measure == Fraction(0)
            case float(f):
                if self.unit == '!' and math.isinf(f):
                    return f > 0.0
                return math.isclose(f, 0.0) and math.isclose(float(self.measure), 0.0)
            case Distance(measure, unit, _):
                if unit == '!':
                    return self.unit == '!'
                if unit != '*' and self.unit != '*':
                    measure = other.to(self.unit).measure
                return self.measure == measure
        # Fall out to fail case
        raise ValueError(f"equality compares are undefined for types Distance and {type(other)}")

    def __le__(self, other) -> bool:
        """Compare for ordering."""
        return (self == other) or (self < other)

    def __gt__(self, other) -> bool:
        """Compare for ordering."""
        return not self <= other

    def logstr(self):
        """Produce a debugging string representation for the logs."""
        # pylint: disable=no-member
        return f"{self.inch:.2f}in"  # type: ignore


def distance_list(*measures, unit: DistanceUnit) -> list[Distance]:
    """Convert a list of numbers to a list of distances expressed in <unit> units."""
    return [Distance(m, unit) for m in measures]


# Make Distance properties that get the measure only in a particular unit.
# ie:  d.in == d in inches, d.pt == d in points ---> as raw _numbers_
#
# THIS WAS A TOTAL PAIN IN THE POSTERIOR:  without the make_lambda function, 'du' was going into the lambda's closure
# so my converters always took on the final DistanceUnit type regardless of when I created them.
# The workaround was to *assign* a value to the self.to parameter variable in a function.
# See the Python rules around "nonlocal" vs "global" for the gist of the whole problem.
#
# can I make a metaclass or a mixin for these measure unit-specific conversion properties ?
#
def make_lambda(du: DistanceUnit) -> Callable[[Distance], float]:
    """
    Create a property function that converts a distance to a plain number in <du> units.

    This function is 100% necessary as wrapper to prevent <du> landing inside the lambda's closure.
    See the Python rules around "nonlocal" vs "global" - it's a very subtle PITA.
    """

    return lambda self: float(self.to(du).measure)

for target_unit in DistanceUnit:
    if target_unit.name in ('pct', 'rest', 'infinite'):  # ignore percent for now.  Don't convert to infinite or 'fill-up' distances
        continue
    converter = make_lambda(target_unit)
    conversion = property(converter, None, None, f"Convert this to a scalar value measured in '{target_unit.name}'.")
    setattr(Distance, target_unit.name, conversion)
    Distance.__annotations__[target_unit.name] = Distance.MeasureType
