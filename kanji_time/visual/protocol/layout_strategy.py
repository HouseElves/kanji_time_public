"""
Define a common interface for layout policy objects.

LayoutStrategy is a protocol for layout algorithms that arrange multiple elements inside a parent extent.

The layout engine provides the available space and a list of measured element sizes; the strategy returns
a layout plan that fits them into space and defines their positions.

This design allows layout policies (like stacking, wrapping, or grid layout) to be modular, testable, and composable.
"""

from typing import Protocol, runtime_checkable

from kanji_time.visual.layout.region import Region, Extent


@runtime_checkable
class LayoutStrategy(Protocol):
    """
    Model a policy for placing rectangular extents into a parent extent that frames them.

    The LayoutStrategy defines the interface for computing spatial layouts in a container.

    All LayoutStrategy instances must implement:
    - `measure()`: Given a list of element extents, compute the minimum bounding box to contain them.
    - `layout()`: Given a target size and list of element sizes, return the actual layout regions to place each element.

    The layout strategy is not responsible for rendering or measuring content — only for allocating space.
    """

    def measure(self, element_extents: list[Extent], fit_elements: Extent) -> Extent:
        """Compute a minimum size of a layout for the passed extents under this strategy."""
        ...  # pragma: no cover

    def layout(self, target_extent: Extent, element_extents: list[Extent], fit_elements: Extent) -> tuple[Extent, list[Region]]:
        """Position the passed extents into <target extent> according to this strategy."""
        ...  # pragma: no cover
