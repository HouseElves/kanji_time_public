# container.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model a container frame that holds other content frames.

    - The container uses a LayoutStrategy instance to position reserved space for its children.
    - The children then do their own layout within the reserved extent.
    - At draw time, we get a region which fixes the containers coordinate system in absolute space.

.. only:: dev_notes

    - Add support for floating child containers & a z-axis one day.

----

.. seealso:: :doc:`dev_notes/container_notes`

----

"""
# pylint: disable=fixme

from collections import defaultdict, namedtuple
from collections.abc import Mapping
import functools
import operator

from reportlab.lib import colors

from kanji_time.utilities.general import no_dict_mutators
from kanji_time.visual.protocol.content import DisplaySurface, RenderingFrame, States
from kanji_time.visual.protocol.layout_strategy import LayoutStrategy
from kanji_time.visual.layout.region import Region, Extent, Pos
from kanji_time.visual.layout.distance import Distance

# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)

ReservedArea = namedtuple('ReservedArea', "element region")

class Container(RenderingFrame):
    """
    Model an interior element on the content tree - a "container" in the sense that owns child content.

    Containers aggregate child results upward.
    For example, a container's state is result of applying an aggregation algorithm to the states of child frames.

    A container uses a passed layout strategy instance to automatically handle block layouts.

    Initialize a container with the following.

    :param element_name: a unique name for the container for the logging stream
    :param requested_size: an estimated amount of space for the container
    :param child_elements: content frames to be laid out and drawn in this container
    :param layout_strategy: aggregated helper to lay out children in an extent

    .. only:: dev_notes

        Issues
        ------

            - can a rendering frame exist in multiple containers?  Well, no, because of its hardcoded state.
            - can I make a rendering frame stateless? or at least externalize the state into a context?
            - does this issue even matter?

    High level class relationships are as follows.

    .. mermaid::
        :name: cd_container
        :caption: Class relationships for a compound rendering frame.

        ---
        config:
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB

            class RenderingFrame {
                <<interface>>
                + begin_page(int page_number) bool*
                + measure(extent: Extent) Extent*
                + do_layout(target_extent: Extent) Region*
                + draw(c: DisplaySurface, region: Region) None*
                + state() States
            }
            class LayoutStrategy{
                <<interface>>
                +measure(list[Extent] element_extents, fit_elements: Extent) Extent
                +layout(Extent target_extent, list[Extent] element_extents, Extent fit_elements) tuple[Extent, list[Region]]
            }
            class Container{
                + begin_page(int page_number) bool
                + measure(extent: Extent) Extent
                + do_layout(target_extent: Extent) Region
                + draw(c: DisplaySurface, region: Region) None
                + state() States
            }
            Container --o LayoutStrategy : layout_strategy
            Container --o "n" RenderingFrame : child_elements

    .. only:: dev_notes

        - Fix the debug rectangle.  Use a style instance for it instead of specific colors.
        - Review how anchoring works within containers.

    """
    DRAW_DEBUG_RECTS = False
    # integrate this with a style instance
    DEBUG_RECT_FILL_COLOR = colors.lightgrey
    DEBUG_RECT_INNER_COLOR = colors.lightblue
    DEBUG_RECT_STROKE_COLOR = colors.darkgray

    # There's anchoring via AnchorPoint to consider within a container.
    def __init__(
            self,
            element_name: str,
            requested_size: Extent,
            child_elements: Mapping[str, RenderingFrame],
            layout_strategy: LayoutStrategy
        ):
        """
        Initialize a container named <element_name> occupying <requested_size> that owns <child_elements> positioned with <layout_strategy>.

            - The <hfit_to> and <vfit_to> instance variables identify child elements that can grow to fit excess layout space.
            - The <sizes> instance variable holds the measured size of each child element.  The <{h|v}fit_to> index into that list.

        """
        # These are required by the protocol
        self._state = States.new
        self._requested_size = requested_size
        self._layout_size = requested_size
        self.content_size = Extent.zero

        # My data
        self.element_name = element_name
        self.layout = {
            child_name: ReservedArea(child_element, Region(origin=Pos.zero, extent=Extent.zero))
            for child_name, child_element in child_elements.items()
        }
        self.sizes: list[Extent] = []
        self.layout_strategy = layout_strategy

    @property
    def child_elements(self) -> Mapping[str, RenderingFrame]:
        """
        Immutable version of the the child elements.

        :return: an immutable dictionary of all the child rendering frames in the container.
        """
        return no_dict_mutators({
            name: area.element
            for name, area in self.layout.items()
        })  # returning a copy

    @property
    def state(self) -> States:
        """
        Produce the current state of the content frame.

        State is synthesized from the state of our child frames.

            - If there's no children then use my own state value
            - If no child has been drawn then take the latest state achieved by any child (REVIEW: why not earliest?)
            - If any child as been drawn (REVIEW: why not all children) then my state is drawn

        Data availability and frame reuse are as follows.

            - If any child has more data to present then I have more data to present
            - If all children have all data consumed then all my data is consumed
            - If any child is reusable then I am reusable (REVIEW: invent a partially reusable state?)

        :return: the current rendering state of the container.

        .. only:: dev_notes

            - is "Partially Reusable" a meaningful state to Container clients? Would it be worth any effort?

        """
        # When there's no children, then use my own state value.
        if not self.layout:
            return self._state
        # State values increase the further along we get in processing.
        # The terminal state has some extra flags for continuation context.
        #  ==> use a fold to obtain the max state achieved by children and all bits set by the children.
        combiner = lambda a, b: (max(a[0], b), a[1] | b)
        all_children_state: tuple[int, int] = functools.reduce(
            combiner,
            (area.element.state for area in self.layout.values()),
            (States.new, States.new)
        )
        if all_children_state[0] < States.drawn:
            return all_children_state[0]

        # From here on, we're in some flavor of terminal state.
        # This container...
        #   - is reusable if any child is reusable  (Review: partially reusable sub-state?),
        #   - has more data if any child has more data, and,
        #   - is consumed if all children are consumed.
        state = States.drawn | (States.reusable & all_children_state[1])
        if States.have_more_data in all_children_state[1]:
            return state | States.have_more_data
        if States.all_data_consumed in all_children_state[1]:
            return state | States.all_data_consumed
        return state

    def resize(self, new_size: Extent) -> Extent:  # pragma: no cover
        """
        Mutate the requested size of the content frame.

        I cannot simply put this into the begin_page logic because I can't easily
        send a new size down to child frames in a container.

        .. only:: dev_notes

            - this method is completely ignored right now.  Axe it?  Implement it?  TBD.

        """
        # Review - ignoring a resize request for now
        _ = new_size
        return new_size

    def begin_page(self, page_number: int) -> bool:
        """
        Signal that the driver is starting a new page and content loading for it should be done now.

        Any necessary
            * content loading
            * layout adjustments
            * new framing elements

        should be done/allocated at this time.

        :param page_number: serial number for each page starting from 1.

        :return: page_available flag - true when there is a page waiting to be generated.

        .. only:: dev_notes

            - I need to either pass begin page down to my children as default handling or obscure it entirely.

        """
        if self.state < States.drawn or States.have_more_data in self.state:
            self._state = States.waiting
            return True
        return False

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the extent of all contained elements and the total extent required to draw them under the layout rules.

            - The container will assume infinite available space if no extent is passed down to it.
            - We'll do two passes on any child that wants to "fit" to available space - the first for it to
              estimate a minimum needed and the second to commit to a size once we've determined the amount
              of space that we can give it.

        :param extent: The size of the usable area on the page - excludes margins and headers/footers.
        :return: The amount of space required for all the page content.

        The measurement algorithm is "evolved code" under review and a little counter-intuitive.
        This sequence diagram highlights the key players for measuring child content for fixed and variable (stretchy) sized
        child elements.

        .. mermaid::
            :name: sd_container_measure
            :caption: Sequence diagram for measuring and stretching children into a container.

            sequenceDiagram
                participant C as Container
                participant L as LayoutStrategy
                participant E1 as Fixed Child
                participant E2 as Stretchy Child

                C->>E1: measure(extent)
                C->>E2: measure(extent) (deferred)
                C->>L: measure(sizes, fit_indices)
                C->>E2: measure(new_extent)
                C->>L: measure(updated_sizes)
                C->>L: layout(target_extent)
                loop for each child
                    C->>Child: do_layout(child_extent)
                end

        .. only:: dev_notes

            - is thread safety on self._state an issue?
            - look at a more more robust way to get lists of extents to the layout strategy.
            - review: this two pass algorithm is absurd!
            - review: do I always want to clamp to my new extent on deferrals?
            - implement measurement constraints
            - not handling failure modes of too much content for the space at all gracefully
              things go wonky when any part of an extent goes negative or even falls below a minimum content threshold.
            - "stretchyness" is really an aspect of distance, that should roll to the element

                - this speaks to a Measurement protocol with L/T/M dimensions, fuzzy/crisp aspects and arithmetic.
                - eh, the element needs to expose a list of variable dimensions and maybe dependencies
                - two sources of variance:  the layout size is a fit_to or percent or the element has intra-dimension deps

            - share-evenly strategy is completely wrong in general. I need a whitespace allocation strategy with the layout.

        """

        self._state = States.needs_layout  # is thread safety an issue?

        assert self.requested_size is not None
        extent = self.requested_size & extent

        # Defer measuring stretchy children until we know how much space to give them.
        # The child might come back with a minimum space or it might just punt
        # and say 'call me later with better information, please' - which we'll do in the second pass.
        deferred: list[tuple[int, RenderingFrame, list[str]]] = []
        fit_to_dims = defaultdict(list)
        self.sizes = []  # yuck!
        for i, (element, _) in enumerate(self.layout.values()):
            if element.is_stretchy.width or element.is_stretchy.height:
                fit_to = []
                if element.is_stretchy.width:
                    fit_to.append("width")
                if element.is_stretchy.height:
                    fit_to.append("height")
                for dim in fit_to:
                    fit_to_dims[dim].append(i)
                deferred.append((i, element, fit_to))
            size = element.measure(extent)
            self.sizes.append(size)

        consumed = self.layout_strategy.measure(self.sizes, Extent(fit_to_dims["width"], fit_to_dims["height"]))

        if deferred:
            # Share the left over page space evenly (or page space shrinkage) evenly.
            leftover = Extent(**{
                dim: (dim_extent - getattr(consumed, dim))/max(1, len(fit_to_dims[dim]))
                for dim, dim_extent in extent._asdict().items()
            })
            # Review:  this loop is a recipe for grief.
            for i, element, fit_to in deferred:
                # <new_extent> is guaranteed to fit inside the target extent by the construction of <leftover>
                # I really need to remeasure!
                # Text regions can vary their height as a function of width. So can isotropic scaling of images.
                # I'm only going to update dimensions that shrink.
                # Review: what about hard-limits?
                new_extent = self.sizes[i] + leftover
                assert new_extent in extent, f"new_extent {new_extent} == {self.sizes[i]} + {leftover} not in extent = {extent}"
                revised_extent = element.measure(new_extent)
                # Review:  not quite right, what about page overflow?  Handle with an exception? Implies a smart distance accumulator?
                new_extent.conditional_replace(operator.__lt__, **revised_extent._asdict())
                # new extent is exactly what you get!
                # Review: could I try to shuffle more slop around if <element> wants more space.
                self.sizes[i] = new_extent  # revised_extent == element.measure(new_extent)

            # Review - passing an extent of lists here is a little wacky.
            consumed = self.layout_strategy.measure(self.sizes, Extent([], []))

        self._layout_size = consumed
        return consumed


    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position all visible element inside the usable page area.

        :param extent: The size of the space provisionally allocated to me.

        :return: region - a private coordinate space for correctly positioning all our elements on a page.

            - region.origin = the offset into the target extent to set the coordinate origin
            - region.extent = the actual rendering size of that content.

        .. only:: dev_notes

            - is thread safety on self._state an issue?
            - look at a more more robust way to get lists of extents to the layout strategy.
            - is this true? "We don't care about inter-element gaps - the frame is responsible for its own explicit margins."
            - do I need to anchor a child in the parent, which affects my computed origin, or myself?


        """
        self._state = States.ready  # is thread safety an issue?

        logging.info(
            "%s.do_layout(%s) - Laying out '%s'",
            self.__class__.__name__,
            ' by '.join(map(lambda x: str(x.inch)+'in', target_extent)),
            self.element_name
        )

        # The layout strategy allocates regions on the page for each element.
        # The element itself must to its own layout to position its origin and its children.
        layout_extent, child_regions = self.layout_strategy.layout(
            target_extent,
            self.sizes,
            Extent([], [])  # Review passing extents of lists
        )
        if len(child_regions) != len(self.layout):  # pragma: no cover
            logging.error(
                "Region count mismatch received from the layout strategy: #regions == %s != %s == #elements",
                len(child_regions),
                len(self.layout)
                )
            raise ValueError("Region count mismatch received from the strategy")

        # We don't care about inter-element gaps - the frame is responsible for its own explicit margins.
        new_layout: dict[str, ReservedArea] = {}
        for (element_name, (element, _)), region in zip(self.layout.items(), child_regions):
            logging.info(
                "\t%s.do_layout(%s) - Laying out child element '%s' in %s",
                self.__class__.__name__, ' by '.join(map(lambda x: str(x.inch)+'in', target_extent)),
                element_name,
                ' by '.join(map(lambda x: str(x.inch)+'in', region.extent))
            )
            assert isinstance(element, RenderingFrame), f"Expected a Content instance, got a {element.__class__.__name__} instance."

            # Review consistency of anchor point usage.
            # Do I need to anchor the child in the parent, which affects my computed origin, or myself?
            element_region = element.do_layout(region.extent)
            new_layout[element_name] = ReservedArea(element, Region(region.origin + element_region.origin, element_region.extent))

            logging.info(
                "\t%s.do_layout(%s) - positioned child element '%s' in %s.",
                self.__class__.__name__, target_extent.logstr(),
                element_name, new_layout[element_name].region.logstr()
            )
        self.layout = new_layout

        return Region(Pos(Distance.zero, Distance.zero), layout_extent)

    def draw(self, c: DisplaySurface, region: Region):
        """
        Draw all my child elements inside the requested area.

            - This is a straight up loop over the children to draw themselves.
            - Note the offset of the child regions by the <parent_origin> - this will
              transform relative coordinates in each region to the parent's coordinate system.

        :param c: a surface that knows how to execute the drawing commands that we send to it.
        :param region: the topmost coordinate space for drawing all the container's child elements.

        .. only:: dev_notes

            - is thread safety on self._state an issue?

        """
        self._state = States.drawn  # is thread safety an issue?

        # Draw the children in the regions we computed for them during layout.
        parent_origin = region.origin
        for (child, child_region) in self.layout.values():
            self.draw_bounding_rect(c, child_region, parent_origin)
            child.draw(c, child_region + parent_origin)

        logging.info("After draw, Container '%s' state = %s", self.element_name, self.state.name)

    def update(self, new_children: Mapping[str, RenderingFrame | None]) -> Mapping[str, RenderingFrame]:
        """
        Modify the child frame-set in-place.

        .. note::
            This is under review as an experimental add for the ReportController abstraction.
            I'm not certain that I like this approach yet; it has all my design spidey-senses tingling.

            - Pass a value of 'None' on a key to remove that named frame from the container.
            - Pass a fresh instance of a frame on a key to replace that named frame
            - Pass a new key to add new frame content

        .. warning::
            This method mutates the internal frame map. Use cautiously.
            It assumes that any changed key has already had its `begin_page()` called.
            Ideally, I'd like to force the container's state into "needs_layout" if `update()` does anything to self.layout().
            Even better: forbid `update` entirely if we're not waiting to layout or finished with a page -
            i.e. the container is in an "intermission" state.

        :param new_children: A mapping of child names to RenderingFrame instances.
        :return: a frozen dictionary of the new child frames
        """
        remove_us = (
            name for (name, element) in new_children.items()
            if name in self.layout and element is None
        )
        add_us = (
            name for (name, element) in new_children.items()
            if (element is not None
                and (name not in self.layout or element is not self.layout[name].element)
            )
        )
        # WARNING: this completely messes with the layout. It's a pretty ugly hack.
        for remove_me in remove_us:
            self.layout.pop(remove_me)
        for add_me in add_us:
            self.layout[add_me] = ReservedArea(new_children[add_me], Extent.zero)
        return self.child_elements

    def draw_bounding_rect(self, c, region, offset):  # pragma: no cover
        """
        Draw a boundary around the container's region.

        Deprecated.
        """
        if self.DRAW_DEBUG_RECTS:
            c.setFillColor(self.DEBUG_RECT_INNER_COLOR)
            c.setStrokeColor(self.DEBUG_RECT_STROKE_COLOR)
            origin, extent = region.origin + offset, region.extent
            c.rect(origin.x.pt, origin.y.pt, extent.width.pt, extent.height.pt, stroke=1, fill=1)

# assert isinstance(Container, RenderingFrame), "Container violates the Content protocol!"
