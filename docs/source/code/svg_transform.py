"""
he svgwrite Transform mixin extracted.
The svgwrite module does not allow you to make one of these independently.
Pshaw, I say.
"""


class Transform:
    """
    The **Transform** mixin operates on the **transform** attribute.
    The value of the **transform** attribute is a `<transform-list>`, which
    is defined as a list of transform definitions, which are applied in the
    order provided. The individual transform definitions are separated by
    whitespace and/or a comma. All coordinates are **user
    space coordinates**.

    """
    transformname = 'transform'
    def __init__(self):
        self.transform = ""

    def translate(self, tx, ty=None):
        """
        Specifies a translation by **tx** and **ty**. If **ty** is not provided,
        it is assumed to be zero.

        :param number tx: user coordinate - no units allowed
        :param number ty: user coordinate - no units allowed
        """
        self._add_transformation(f"translate({', '.join(map(str,  [tx, ty] ))})")

    def rotate(self, angle, center=None):
        """
        Specifies a rotation by **angle** degrees about a given point.
        If optional parameter **center** are not supplied, the rotate is
        about the origin of the current user coordinate system.

        :param number angle: rotate-angle in degrees
        :param 2-tuple center: rotate-center as user coordinate - no units allowed

        """
        self._add_transformation(f"rotate({','.join(map(str,  [angle, center] ))})")

    def scale(self, sx, sy=None):
        """
        Specifies a scale operation by **sx** and **sy**. If **sy** is not
        provided, it is assumed to be equal to **sx**.

        :param number sx: scalar factor x-axis, no units allowed
        :param number sy: scalar factor y-axis, no units allowed

        """
        self._add_transformation(f"scale({','.join(map(str, [sx, sy]))})")

    def skewX(self, angle):  # pylint: disable=invalid-name
        """ Specifies a skew transformation along the x-axis.

        :param number angle: skew-angle in degrees, no units allowed

        """
        self._add_transformation(f"skewX({angle})")

    def skewY(self, angle):  # pylint: disable=invalid-name
        """ Specifies a skew transformation along the y-axis.

        :param number angle: skew-angle in degrees, no units allowed

        """
        self._add_transformation(f"skewY({angle})")

    def matrix(self, a, b, c, d, e, f):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """ Specifies a coordinate transform directly as a matrix."""
        self._add_transformation(f"matrix({','.join(map(str,  [a, b, c, d, e, f] ))})")

    def _add_transformation(self, new_transform):
        old_transform = self.transform
        self.transform = f"{old_transform.strip()} {new_transform.strip()}"

    def __str__(self):
        return self.transform
