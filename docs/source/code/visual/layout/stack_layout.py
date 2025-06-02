"""
Define a layout strategy that places content frames in a horizontal or vertical stack.

A ContentFrame/Container instance uses a StackLayoutStrategy to place all of its child frames in a single row or column.

A strategy instance **never** owns any content frame.  It strictly operates only on a set of dimensions and constraints to produce
a layout - a/k/a a set of *regions* - corresponding to these dimensions.

The key benefit for this separation of responsibility is to gracefully handle variable size (a/k/a "fit-to" or "stretchy") dimensions
without cluttering the logic in the Container's layout algorithm.

Assumptions
-----------

The assumptions in a StackLayout are:

    - each content frame is rectangular,
    - there is a *stack_dim* which is the dimension along which the strategy juxtaposes frame,
    - there is an *other_dim* which is the "free" dimension that does not receive neighbors, and,
    - there is an (x, y) position for each content frame - which for stacks is 0 on the "other_dim" and increasing on the "stack_dim".

Since I want to reuse these ideas in a grid layout, I don't make any assumption about the content of a position to exploit the the 4th point
above.

Helpers
-------

The stack layout defines a number of helper functions for "stack vs other" so that horizontal & vertical stacking use the same logic.
(NB: this is probably design overkill/overly complex, but it was an interesting tactic to explore.)

    - get_stack_pos, get_other_pos: extracts the index in the "stack" or "other" direction from a Pos instance.
    - get_stack_dim, get_other_dim: extracts the length of a content frame in the "stack" or "other" direction.
    - make_extent, make_pos: converts an ordered pair if (stack, other) to a well-formed Extent or Pos with "stack" and "other" in the
      correct position for width/height or x/y, respectively.
    - stack_idx: the index into a tuple for a "stack" value.  (There is an implicit assumption is the "other" value is at 1 - stack_idx.)

Class Relationships
-------------------

The stack layout strategy fits into the general pagination and layout model as a realization of the LayoutStrategy interface.

.. mermaid::
    :name: cd_stack_layout
    :caption: Class relationships for a stacked layout strategy.

    ---
    config:
        mermaid_include_elk: "0.1.7"
        layout: elk
        class:
            hideEmptyMembersBox: true
    ---
    classDiagram
        direction TD

        class Container {
            <<realization: RenderingFrame>>
            + begin_page(int page_number) bool
            + measure(extent: Extent) Extent
            + do_layout(target_extent: Extent) Region
            + draw(c: DisplaySurface, region: Region) None
            + state() States
        }

        Container --* "n" RenderingFrame : children
        Container --* LayoutStrategy : uses for presentation layout calculations
        RenderingFrame <.. StackLayoutStrategy: arranges in a line using their dimensions as a proxy


        class LayoutStrategy {
            <<interface>>
            +measure(list~Extent~ element_extents,  Extent fit_elements) Extent*
            +layout(Extent target_extent, list~Extent~ element_extents, Extent fit_elements) (Extent, list~Region~)*
        }
        class StackLayoutStrategy
        LayoutStrategy <|-- StackLayoutStrategy
        class StackLayoutStrategy {
            <<realization>>
            +measure(list~Extent~ element_extents,  Extent fit_elements) Extent
            +layout(Extent target_extent, list~Extent~ element_extents, Extent fit_elements) (Extent, list~Region~)
        }

.. only:: dev_notes

    - are get_stack_pos, get_other_pos misnamed? get_{stack|other}_idx instead?

----

.. seealso:: :doc:`dev_notes/stack_layout_notes`

----


"""

  # pylint: disable=fixme

from collections.abc import Callable
from itertools import accumulate
from enum import Enum

from visual.layout.region import Region, Extent, Pos
from visual.layout.distance import Distance


class StackDirection(Enum):
    """Define the possible directions for a stack: up or down."""
    # pylint: disable=invalid-name
    horizontal = "horizontal"
    vertical = "vertical"


class StackLayoutStrategy:
    """
    Stack child elements horizontally or vertically.

    Initialize a StackLayoutStrategy instance with the following.

    :param direction: "horizontal" to stack frames left-to-right, "vertical" to stack frames top-to-bottom.

    Class Relationships
    -------------------

    A StackLayout is a no-frills implementation of LayoutStrategy that exploits the features of the geometry to arrange content frames.

    .. mermaid::
        :name: cd_stack_layout_detail
        :caption: Class relationship details for a stacked layout strategy.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TD

            class LayoutStrategy {
                <<interface>>
                +measure(list~Extent~ element_extents,  Extent fit_elements) Extent*
                +layout(Extent target_extent, list~Extent~ element_extents, Extent fit_elements) (Extent, list~Region~)*
            }
            class StackLayoutStrategy
            LayoutStrategy <|-- StackLayoutStrategy
            class StackLayoutStrategy {
                <<realization>>
                +measure(list~Extent~ element_extents,  Extent fit_elements) Extent
                +layout(Extent target_extent, list~Extent~ element_extents, Extent fit_elements) (Extent, list~Region~)
            }

            class GeometryHelpers {
                <<embedded methods>>
                +get_stack_pos(Pos pos) Distance
                +get_other_pos(Pos pos) Distance
                +get_stack_dim(Extent size) Distance
                +get_other_dim(Extent size) Distance
                +make_extent(Distance stack, Distance other) Extent
                +make_pos(Distance stack, Distance other) Pos
                +stack_idx() int
            }

            StackLayoutStrategy ..> GeometryHelpers : abstracts stack direction using

            RenderingFrame "n" ..> "n" FrameDimensions : extracted by their parent container
            FrameDimensions "n" <.. StackLayoutStrategy: arranges in a line
            Region "n" <.. StackLayoutStrategy: produces drawing coordinates
            Region <..> FrameDimensions : correspond

    .. only:: dev_notes

        - Add options to the initializer for inter-element spacing?

            - would this be subsumed by a companion whitespace allocator strategy?
            - number of slop-fit element and slop-allocation  [NO: this is baked into Distance]
            - support for percentages [NO: this is on the Distance wish-list]

        - Some of these may be global to all layout strategies.
        - horizontal/vertical helper methods should come as a mix-in so anybody can use them.

    """

    # plug in functions for horizontal vs vertical strips.
    # This should be a "Direction" mix-in.
    hv_direction_methods = {
        "horizontal": {
            "get_stack_pos": lambda pos: pos.x,
            "get_other_pos": lambda pos: pos.y,
            "get_stack_dim": lambda x: x.width,
            "get_other_dim": lambda x: x.height,
            "make_extent": Extent,  # uses default arg order
            "make_pos": Pos,  # uses default arg order
            "stack_idx": lambda : 0,
        },
        "vertical": {
            "get_stack_pos": lambda pos: pos.y,
            "get_other_pos": lambda pos: pos.x,
            "get_stack_dim": lambda x: x.height,
            "get_other_dim": lambda x: x.width,
            "make_extent": lambda s, o: Extent(o, s),
            "make_pos": lambda s, o: Pos(o, s),
            "stack_idx": lambda : 1,
        }
    }

    get_stack_pos: Callable[[Pos], Distance] = lambda pos: Distance.zero
    get_other_pos: Callable[[Pos], Distance] = lambda pos: Distance.zero
    get_stack_dim: Callable[[Extent], Distance] = lambda x: Distance.zero
    get_other_dim: Callable[[Extent], Distance] = lambda x: Distance.zero
    make_extent: Callable[[Distance, Distance], Extent] = lambda s, o: Extent(Distance.zero, Distance.zero)
    make_pos: Callable[[Distance, Distance], Pos] = lambda s, o: Pos(Distance.zero, Distance.zero)
    stack_idx: Callable[[], int] = lambda : -1

    def __init__(self, direction: str):

        if direction not in self.hv_direction_methods:
            raise ValueError(f"Unrecognized strip direction: '{direction}'")
        self.direction = direction

        # For measuring the content
        for fname, func in self.hv_direction_methods[direction].items():
            setattr(self, fname, func)

    def measure(self, element_extents: list[Extent], fit_elements: Extent) -> Extent:
        """
        Compute the minimum size of this layout with the passed child sizes.

        In the stacked layout, this minimum size is:

            - the sum of the dimensions in the stacking direction
            - the max of the dimensions in the other direction

        This strategy regards the passed "fit to" dimensions as minimums, so these are included in the measure.

        :param element_extents: the size of each element to be positioned
        :param fit_elements: indices into <element_extents> that are stretchy/fit-to dimensions
        :return: the minimum page extent required for the stacked rectangles
        """
        stacked_fit_to = self.get_stack_dim(fit_elements)  # pylint: disable=unused-variable
        other_fit_to = self.get_other_dim(fit_elements)  # pylint: disable=unused-variable

        stacked_dim: Distance = sum((
            self.get_stack_dim(element_extent)
            for i, element_extent in enumerate(element_extents)
            # if i not in stacked_fit_to
            ),
            start=Distance.zero
        )
        other_dim: Distance = max(
            self.get_other_dim(element_extent)
            for i, element_extent in enumerate(element_extents)
            # if i not in other_fit_to
        )

        return self.make_extent(stacked_dim, other_dim)

    def layout(self, target_extent: Extent, element_extents: list[Extent], fit_elements: Extent) -> tuple[Extent, list[Region]]:
        """
        Position each element in the final stack.

        During layout, we remeasure the passed frame dimensions to get their total minimum bounds.
        The task of this method is to allocated any excess ('slop') space in the total_extent above this minimum to the fit-to elements.

        :param target_extent: the amount of space allocated for the final layout
        :param element_extents: the amount of space allocated to each element in the layout
        :param fit_elements: indices into <element_extents> that are stretchy/fit-to dimensions

        :return: the total extent occupied by the elements and their positioned regions.

        .. note:: The returned total extent occupied may exceed the passed total extent.
                  It's up to the container to decide how to handle this case.

        .. only:: dev_notes

            - is it appropriate to throw a `LayoutOverflow` exception up to my caller?  gut says "no way!" - use a boolean "clip" setting.
            - without an exception, the caller will need to check the return values
            - without clipping I'll be getting an implicit z-order!
            - pylint is complaining about the number of locals - factor out some functionality?

        """

        fit_to: list[int] = fit_elements[self.stack_idx()]

        # Allocate slop space to the slop fit elements.
        minimum_size = self.measure(element_extents, fit_elements)
        total_stacked = self.get_stack_dim(minimum_size)
        slop_fit = Distance.zero
        # what if total_extent is too small? Totally ignored for now.
        if self.get_stack_dim(target_extent) > total_stacked and len(fit_to) > 0:
            slop_fit = (self.get_stack_dim(target_extent) - total_stacked) // len(fit_to)
            total_stacked = self.get_stack_dim(target_extent)

        stacked_dims = [
            self.get_stack_dim(extent) + (slop_fit if i in fit_to else Distance.zero)
            for i, extent in enumerate(element_extents)
        ]

        # origin in the lower left
        # Review: disregard (? could be weird for UX ?) elements with a zero stack dimension
        #       --> they don't render so don't contribute to the other dimension
        origin = Pos(Distance.parse("0pt"), Distance.parse("0pt"))
        child_regions = []
        for stacked_pos, stacked_dim in zip(accumulate(stacked_dims, initial=self.get_stack_pos(origin)), stacked_dims):
            layout_extent = self.make_extent(stacked_dim, self.get_other_dim(target_extent))
            layout_pos = self.make_pos(stacked_pos, self.get_other_pos(origin))
            child_regions.append(Region(layout_pos, layout_extent))
            origin = layout_pos
        max_other = max(map(self.get_other_dim, map(lambda x: x.extent, child_regions)))
        return self.make_extent(total_stacked, max_other), child_regions


if __name__ == '__main__':  # pragma: no cover
    extents = [
        Extent(Distance.parse("100pt"), Distance.parse("110pt")),
        Extent(Distance.parse("*"), Distance.parse("220pt")),
        Extent(Distance.parse("300pt"), Distance.parse("330pt")),
        Extent(Distance.parse("400pt"), Distance.parse("*")),
    ]
    fit_to_test = Extent([1], [3])

    vlayout = StackLayoutStrategy("vertical")
    vertical_size = vlayout.measure(extents, fit_to_test)
    assert vertical_size == Extent(Distance.parse("400pt"), Distance.parse("660pt")), f"Unexpected vertical size = {vertical_size}."
    consumed, vertical_regions = vlayout.layout(vertical_size, extents, fit_to_test)
    assert consumed == vertical_size
    assert vertical_regions[3].extent.height.pt == 0
    consumed, vertical_regions = vlayout.layout(2*vertical_size, extents, fit_to_test)
    assert consumed == 2*vertical_size
    assert vertical_regions[3].extent.height.pt == vertical_size.height.pt

    hlayout = StackLayoutStrategy("horizontal")
    horizontal_size = hlayout.measure(extents, fit_to_test)
    assert horizontal_size == Extent(Distance.parse("800pt"), Distance.parse("330pt")), f"Unexpected horizontal size = {horizontal_size}."
    consumed, horizontal_regions = hlayout.layout(horizontal_size, extents, fit_to_test)
    assert consumed == horizontal_size
    assert horizontal_regions[1].extent.width.pt == 0
    consumed, horizontal_regions = hlayout.layout(2*horizontal_size, extents, fit_to_test)
    assert consumed == 2*horizontal_size
    assert horizontal_regions[1].extent.width.pt == horizontal_size.width.pt
