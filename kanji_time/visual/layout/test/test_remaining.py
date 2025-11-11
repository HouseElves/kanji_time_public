# test_remaining.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test suite for AnchorPoint, PageSettings, and PaperNames modules with full branch coverage."""

import pytest
from reportlab.lib.pagesizes import A4, LETTER
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.paper_names import PaperNames, PaperOrientations
from kanji_time.visual.frame.page import Page


# Anchor Point Tests ----------------------------------------------------------------------------------------------------------------------- #


def test_anchor_point_values():
    """
    Test all defined AnchorPoint values.

    REQ: The anchor point type identifies a relative position in a rectangle using the 8 compass directions N, NE, E, SE, S, SW, W, NW
         and CENTER as labels.
    """
    assert AnchorPoint.CENTER in AnchorPoint
    assert AnchorPoint.N in AnchorPoint
    assert AnchorPoint.E in AnchorPoint
    assert AnchorPoint.S in AnchorPoint
    assert AnchorPoint.W in AnchorPoint
    assert AnchorPoint.SE in AnchorPoint
    assert AnchorPoint.NE in AnchorPoint
    assert AnchorPoint.NW in AnchorPoint
    assert AnchorPoint.SW in AnchorPoint


def test_anchor_point_center_zero():
    """
    Test all defined AnchorPoint values.

    REQ: The CENTER label is the unique label with a bit representation of 0.
    """
    assert AnchorPoint.CENTER.value == 0
    assert AnchorPoint.N.value != 0
    assert AnchorPoint.E.value != 0
    assert AnchorPoint.S.value != 0
    assert AnchorPoint.W.value != 0
    assert AnchorPoint.SE.value != 0
    assert AnchorPoint.NE.value != 0
    assert AnchorPoint.NW.value != 0
    assert AnchorPoint.SW.value != 0


def test_anchor_point_cardinal_unique_bits():
    """
    Test all defined AnchorPoint values.

    REQ: The N, S, E, W cardinal direction labels each have distinct bits set from the others.
    """
    not_N = AnchorPoint.E | AnchorPoint.S | AnchorPoint.W
    assert not_N.value != 0
    assert (AnchorPoint.N & not_N).value == 0, f"AnchorPoint.N & not_N == {AnchorPoint.N & not_N} == {(AnchorPoint.N & not_N).value}"

    not_E = AnchorPoint.N | AnchorPoint.S | AnchorPoint.W
    assert not_E.value != 0
    assert (AnchorPoint.E & not_E).value == 0, f"AnchorPoint.E & not_E == {AnchorPoint.E & not_E} == {(AnchorPoint.E & not_E).value}"

    not_S = AnchorPoint.E | AnchorPoint.N | AnchorPoint.W
    assert not_S.value != 0
    assert (AnchorPoint.S & not_S).value == 0, f"AnchorPoint.S & not_S == {AnchorPoint.S & not_S} == {(AnchorPoint.S & not_S).value}"

    not_W = AnchorPoint.E | AnchorPoint.S | AnchorPoint.N
    assert not_W.value != 0
    assert (AnchorPoint.W & not_W).value == 0, f"AnchorPoint.W & not_W == {AnchorPoint.W & not_W} == {(AnchorPoint.W & not_W).value}"

    assert len({AnchorPoint.N.value, AnchorPoint.E.value, AnchorPoint.S.value, AnchorPoint.W.value}) == 4
    assert len({not_N.value, not_E.value, not_S.value, not_W.value}) == 4


def test_anchor_point_non_cardinal_combined_bits():
    """
    Test all defined AnchorPoint values.

    REQ: THE NE, SE, SW, NW labels have distinct bitwise representations that are the bitwise 'or' of their cardinal direction representations.
    """
    cardinal = {AnchorPoint.N, AnchorPoint.E, AnchorPoint.S, AnchorPoint.W}
    diagonal = {AnchorPoint.NE, AnchorPoint.SE , AnchorPoint.SW , AnchorPoint.NW}
    assert len(diagonal) == 4
    assert len(diagonal - cardinal) == 4

    assert AnchorPoint.SE == (AnchorPoint.S | AnchorPoint.E)
    assert AnchorPoint.NE == (AnchorPoint.N | AnchorPoint.E)
    assert AnchorPoint.NW == (AnchorPoint.N | AnchorPoint.W)
    assert AnchorPoint.SW == (AnchorPoint.S | AnchorPoint.W)


def test_anchor_point_combinations():
    """Test combining AnchorPoint flags."""
    combined = AnchorPoint.N | AnchorPoint.E
    assert combined == AnchorPoint.NE
    combined = AnchorPoint.S | AnchorPoint.W
    assert combined == AnchorPoint.SW

def test_anchor_point_invalid_combination():
    """
    Test invalid flag combination doesn't match valid anchor points.

    REQ: Attempting to instantiate an anchor point type with an unknown combination of representation bits yields a value error exception.
    """
    with pytest.raises(ValueError):
        _ = AnchorPoint(16)  # No defined anchor point has this flag


def test_anchor_point_membership():
    """
    Test membership in AnchorPoint combinations.

    REQ: The anchor point type provides an 'in' operator that tests for bits set in label representations.
    """
    combined = AnchorPoint.N | AnchorPoint.S
    assert AnchorPoint.N in combined
    assert AnchorPoint.S in combined
    assert AnchorPoint.E not in combined
    assert AnchorPoint.NW not in combined


# Page Setting Tests ----------------------------------------------------------------------------------------------------------------------- #


def test_page_settings_initialization():
    """
    Test initialization of default PageSettings.

    REQ: The page settings type can be instantiated with no parameters using well-known default settings.
    """
    settings = Page.factory().settings
    assert settings.margins.left == settings.margins.right == settings.margins.top == settings.margins.bottom
    assert settings.page_size.width > 0
    assert settings.page_size.height > 0

def test_page_settings_usable_area():
    """
    Test calculation of usable area based on margins.

    REQ: The page setting type has an extent property containing the usable page size which is the physical page size less the page margins.
    """
    settings = Page.factory().settings
    expected_width = settings.page_size.width - (settings.margins.left + settings.margins.right)
    expected_height = settings.page_size.height - (settings.margins.top + settings.margins.bottom)
    assert settings.printable_region.extent.width == expected_width
    assert settings.printable_region.extent.height == expected_height


# Paper Names Tests ------------------------------------------------------------------------------------------------------------------------ #


def test_paper_names_enum():
    """
    Test that PaperNames enumeration maps correctly to ReportLab sizes.

    REQ: The paper names type assigns matching labels to page sizes specified by ReportLab.
    REQ: Labels in the paper names type have a value corresponding to the paper size defined by ReportLab as an ordered pair of floats
         containing point measures of width by height.
    """
    assert PaperNames.A4.value == A4
    assert PaperNames.LETTER.value == LETTER

def test_paper_orientations():
    """
    Test orientation transformations on paper sizes.

    REQ: The paper orientations type assigns labels to the landscape (width > height) and portrait (height >= width) page orientations.
    REQ: Labels in in the paper orientations type contain functions mapping paper sizes to a width, height pair for that orientation.
    """
    size = PaperNames.A4.value
    portrait_size = PaperOrientations.portrait(size)
    landscape_size = PaperOrientations.landscape(size)
    assert portrait_size[1] >= portrait_size[0]  # Height should be greater than or equal to width
    assert landscape_size[0] >= landscape_size[1]  # Width should be greater than or equal to height

def test_paper_names_completeness():
    """
    Ensure all important paper sizes are present in the enum.

    REQ: The paper names type contains labels for at least the common paper sizes of A4, LETTER, LEGAL and TABLOID.
    """
    assert PaperNames.A4 in PaperNames
    assert PaperNames.LETTER in PaperNames
    assert PaperNames.LEGAL in PaperNames
    assert PaperNames.TABLOID in PaperNames

def test_invalid_paper_orientation():
    """
    Test passing invalid paper size to orientation functions raises an error.

    REQ: Passing a non-size instance to a paper orientation label function yields a type error exception.
    """
    with pytest.raises(TypeError):
        PaperOrientations().portrait("invalid_size")
