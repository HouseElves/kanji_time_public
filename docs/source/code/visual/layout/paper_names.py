"""
Provide named paper sizes and orientation helpers compatible with ReportLab.

This is purely a convenience module to wrap ReportLab's raw paper size tuples into a Python-friendly form.
I choose an Enum instance (`PaperNames`), to enable developers to reference sizes like `PaperNames.A4` or `PaperNames.LETTER` by name.

There is also singleton (`PaperOrientations`) that has rotation services to produce portrait vs landscape page orientations.

The intended consumer of these is the `PageSettings` class.
They are equally applicable in any scenario that needs to specify page size symbolically or by English name.

Licensing
---------

This file wraps and re-exports page size constants from ReportLab.
Original values sourced from reportlab.lib.pagesizes

ReportLab is licensed under a BSD-style license:
https://www.reportlab.com/devfaq/license/

Copyright (c) 2000-2023, ReportLab Inc. All rights reserved.

----
"""


from collections.abc import Callable
from enum import Enum
from reportlab.lib import pagesizes

from utilities.singleton import SingletonMeta


PageSize = tuple[float, float]  #: ReportLab's page size measurement type
PaperOrientation = Callable[[PageSize], PageSize]  #: Signature for ReportLab's page orientation helper functions


class PaperOrientations(metaclass=SingletonMeta):  # pylint: disable=too-few-public-methods
    """
    Modify a page size so its longer edge is east-west (portrait) or north-south (landscape).

    This is a Singleton wrapper around ReportLab's portrait() and landscape() helpers.

    These functions rotate a (width, height) tuple such that for:
        - portrait(): height > width, and,
        - landscape(): width > height.
    """
    portrait: PaperOrientation = pagesizes.portrait  # pylint: disable=invalid-name
    landscape: PaperOrientation = pagesizes.landscape  # pylint: disable=invalid-name


class PaperNames(Enum):
    """
    Express common paper sizes imported from ReportLab (as tuples) as enumerated constants.

    Each entry (e.g., `A4`, `LETTER`) provides a `(width, height)` tuple in points, suitable for PDF layout.

    .. note:: lowercase aliases (e.g., `letter`) are included for backward compatibility but deprecated by ReportLab.
    """
    # ISO Paper sizes

    A0 = pagesizes.A0
    A1 = pagesizes.A1
    A2 = pagesizes.A2
    A3 = pagesizes.A3
    A4 = pagesizes.A4
    A5 = pagesizes.A5
    A6 = pagesizes.A6
    A7 = pagesizes.A7
    A8 = pagesizes.A8
    A9 = pagesizes.A9
    A10 = pagesizes.A10

    B0 = pagesizes.B0
    B1 = pagesizes.B1
    B2 = pagesizes.B2
    B3 = pagesizes.B3
    B4 = pagesizes.B4
    B5 = pagesizes.B5
    B6 = pagesizes.B6
    B7 = pagesizes.B7
    B8 = pagesizes.B8
    B9 = pagesizes.B9
    B10 = pagesizes.B10

    C0 = pagesizes.C0
    C1 = pagesizes.C1
    C2 = pagesizes.C2
    C3 = pagesizes.C3
    C4 = pagesizes.C4
    C5 = pagesizes.C5
    C6 = pagesizes.C6
    C7 = pagesizes.C7
    C8 = pagesizes.C8
    C9 = pagesizes.C9
    C10 = pagesizes.C10

    # American paper sizes
    LETTER = pagesizes.LETTER
    LEGAL = pagesizes.LEGAL
    ELEVENSEVENTEEN = pagesizes.ELEVENSEVENTEEN

    # From https://en.wikipedia.org/wiki/Paper_size
    JUNIOR_LEGAL = pagesizes.LEGAL
    HALF_LETTER = pagesizes.LETTER
    GOV_LETTER = pagesizes.LETTER
    GOV_LEGAL = pagesizes.LEGAL
    TABLOID = pagesizes.TABLOID
    LEDGER = pagesizes.LEDGER

    # lower case is deprecated as of 12/2001, but here
    # for compatibility
    letter = pagesizes.letter  # pylint: disable=invalid-name
    legal = pagesizes.legal  # pylint: disable=invalid-name
    elevenSeventeen = pagesizes.elevenSeventeen  # pylint: disable=invalid-name
