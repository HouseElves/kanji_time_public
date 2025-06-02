"""
Compass-style alignment flags used to anchor content frames within their parent containers.

The AnchorPoint enum uses bit flags to express positions like `N`, `SW`, or `CENTER` to the layout logic.

The intended consumer of an AnchorPoint instance is Extent.anchor_at(); which uses it as a hint for placing a smaller extent
inside a larger one.

----
"""

import enum

class AnchorPoint(enum.Flag):
    """
    Specify how a child content frame should be placed inside a parent container frame.

    The AnchorPoint values follow compass-style names:
        - N, S, E, W: cardinal directions
        - NE, NW, SE, SW: corner alignments
        - CENTER (0): center-aligned in both axes

    These values can be combined using bitwise OR:
        AnchorPoint.N | AnchorPoint.W → NW (top-left)
    """
    CENTER = 0
    N = 1
    E = 2
    NE = 3
    S = 4
    SE = 6
    W = 8
    NW = 9
    SW = 12
