"""Define a custom frame for the summary portion of the Kanji Summary banner."""

from typing import cast
from collections.abc import Sequence
from operator import attrgetter
import itertools
import logging

from reportlab.platypus import Paragraph

from kanji_time.visual.frame.empty_space import EmptySpace
from kanji_time.visual.frame.formatted_text import FormattedText
from kanji_time.visual.frame.simple_element import SimpleElement
from kanji_time.visual.layout.anchor_point import AnchorPoint
from kanji_time.visual.layout.distance import Distance
from kanji_time.visual.layout.region import Extent, Pos, Region
from kanji_time.visual.protocol.content import DisplaySurface, RenderingFrame, States


class KanjiSummary(SimpleElement):
    """
    Represents the contents of the center of the kanji information sheet banner.

        * This pane has a short definition for the kanji in larger bold centered text
        * Underneath, we give on/kun readings and an indication of the kanji frequency left justified in standard sized text.

    I do the layout for this frame by hand.  Can/should this process can be abstracted out to a "text layout" strategy?

    :param requested_size:  The total layout extent to reserve for this element, if possible.
    :param summary_text: - a sequence of ReportLab paragraphs containing top-down text content.

    .. mermaid::
        :name: cd_infosheet_kanji
        :caption: Class relationships for the kanji information report summary.

        ---
        config:
            mermaid_include_elk: "0.1.7"
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        classDiagram
            direction TB
            class RenderingFrame
            class SimpleElement

            <<interface>> RenderingFrame
            <<abstract>> SimpleElement
            RenderingFrame <|-- SimpleElement
            SimpleElement <|-- KanjiSummary

            class KanjiSummary {
                +measure(self, Extent extent) Extent
                +do_layout(self, Extent target_extent) Region
                +draw(self, DisplaySurface c, Region region)
            }
            <<realization>> KanjiSummary
            KanjiSummary --* "3" FormattedText : children
            KanjiSummary --* "3" Region : regions
            KanjiSummary --* Extent : content_size

    """

    def __init__(self, requested_size: Extent, summary_text: Sequence[Paragraph]):
        """
        Initialize the summary paragraph as a heading + body.

        We assume the summary is a sequence of ReportLab paragraphs with the heading in the first one.
        The trick is that I want to have a blank line of whitespace after the heading of approximately the heading's height.

        .. note::

            Estimating text size without a width is a sketchy business.  Paragraph.minWidth is not as useful as one would hope.
            Since we need such an estimate for <requested_size> in the initializers for <self.heading> and <self.body>,

                - we'll take a conservative estimate on height as 1/line per paragraph of <style.leading> points, and,
                - we'll mark the width as "fit to" and let our owning container figure it out at measure time.

        .. only:: dev_notes

            - touching self._requested_size isn't good.  Consider abstracting with a forwarding getter/setter.

                - maybe @forwarded_read(), @forwarded_write, or a Forwarding() class

        """
        super().__init__(requested_size)
        self.content_size = Extent.zero

        # the requested size is for my entire layout. I want a heading with blank line then the body text.
        # Hold them in two distinct FormattedText frames.
        # 1st, copy my requested layout size so I can divide it up
        self.regions = {
            'heading': Region(Pos.zero, Extent.zero),
            'spacer': Region(Pos.zero, Extent.zero),
            'body': Region(Pos.zero, Extent.zero),
        }
        self.children: dict[str, RenderingFrame]  = {
            'heading': FormattedText(Extent.zero, AnchorPoint.N, []),
            'spacer': EmptySpace(Extent.zero),
            'body': FormattedText(Extent.zero, AnchorPoint.W, []),
        }

        if not summary_text:
            logging.warning("No banner text passed the Kanji Summary!  Allocating zero-space text frames.")
            return

        # Reserve space for my text using the style.leading metric.
        # this is only a rough lower bound:  two lines for heading and one line per paragraph in the body.
        # the roughness is OK, we just need a layout hint better than zero.
        #
        # I'm probably better off with EmptySpace frames to do padding and putting all of my children into a container frame.
        heading, *body = summary_text
        heading_pad = Distance(heading.style.leading, "pt")

        heading_height = Distance(heading.style.leading, "pt", at_least=True)
        body_height = Distance(sum(paragraph.style.leading for paragraph in body), "pt", at_least=True)

        self.children = {
            'heading': FormattedText(Extent(Distance.fit_to, heading_height), AnchorPoint.N, [heading]),
            'spacer': EmptySpace(Extent(Distance.fit_to, heading_pad)),
            'body': FormattedText(Extent(Distance.fit_to, body_height), AnchorPoint.W, body),
        }
        self._requested_size = Extent(  # yuck!  Re-init?  Defer init?  Touching privates without permission is a no-no.
            Distance.fit_to,
            max(heading_height + heading_pad + body_height, self.requested_size.height)
        )
        self.content_size = heading_height + heading_pad + body_height
        return

    def measure(self, extent) -> Extent:
        """
        Measure the minimum size around all the content in the Kanji Summary element.

        We need room for the centered heading, a blank line,  and the left justified extra text below the heading.

        :param extent: The estimated size for this element in the final layout - the extent.width is critical to computing text height.

        :return: min_size - the amount of space required for the content as determined by the passed extent, the requested size at
            initialization, and the text content.

        .. only:: dev_notes

            - there's occupied space and then there's whitespace.  measure() returns the required occupied + whiteness.
              there needs to be a way to differentiate these.  Maybe pass both back?  Distance constraints come into play.
            - put the attrgetters below as classmethods on the geometry classes.
            - do I still need to worry about changing my whitespace handling in measure()?  See the dev notes RST.
            - use my coalesce helpers for distance instead of 'or <value>'?  (and where did these helpers disappear to?)

        """
        self._state = States.needs_layout

        width = attrgetter('width')  # put this on the geometry classes
        height = attrgetter('height')  # put this on the geometry classes
        content_extent = attrgetter('content_size')

        # I'll measure text to be as wide as my owner wants it be but cap the height at my requested space.
        # I won't overflow my requested height unless I explicitly measure it so later.
        estimated_size = Extent(
            max(self.requested_size.width, extent.width),
            min(self.requested_size.height, extent.height)
        )

        # If have no content, then commit my measured layout size to be the estimate.
        if not any((content for content in self.children.values())):
            return super().measure(estimated_size)

        child_extents = [
            # this is a little wonky b/c I'm not pulling out occupied space by prior elements --> STILL TRUE??
            # -----> Do I still intend on pulling all the whitespace considerations and size requests out of measure.
            content.measure(extent) for content in self.children.values()
        ]

        # if the passed extent is empty then estimated our minimum required size
        if not extent:
            # I did this right the first time:  Paragraph.minWidth is pretty dumb.  Don't use it to pass along to wrap()
            min_width = max(map(width, child_extents))
            min_height = self.requested_size.height or Distance.fit_to  # don't I already have a coalesce helper?
            self.content_size = Extent(min_width, min_height)
            return super().measure(self.content_size)

        assert extent, "Expected an allocated extent from the owner element"
        assert self.requested_size.width == Distance.fit_to, f"Expected a 'fit to' width, not {self.requested_size.width}"

        self.content_size = Extent(
            max(map(width, map(content_extent, self.children.values()))),
            sum(map(height, map(content_extent, self.children.values())))
        )
        result = Extent(self.content_size.width, max(self.content_size.height, self.requested_size.height))
        logging.info("new measure = %s", result)
        return super().measure(result)

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position the Kanji Summary element inside the owning content frame instance within the target extent.

        :param target_extent: - the size of the bounding rectangle allocated to this frame instance.

        :return: region - a private coordinate space for correctly positioning this element in the target extent

            - `region.origin` = the offset into the target extent to set the coordinate origin
            - `region.extent` = the actual rendering size of that content.

        .. only:: dev_notes

            - Overflows - ReportLab handles text that doesn't fit for us, but that won't be true on all platforms.
              we'll need a way to trap text that doesn't fit and hold it for the future in the general case.
            - Review: I need inheritable unit converters - so I can propagate them outwards to Pos, Extent and Region.

        """
        self._state = States.ready

        if not cast(FormattedText, self.children['heading']).text and not cast(FormattedText, self.children['body']).text:
            return Region(Pos.zero, target_extent)

        # The region is the total height occupied by the child text frames by the passed extent width.
        # For the general case of a text container, I need to trap overflow and save it for the next page
        # What about tiled layouts and flowing text across a bunch of rectangles?  Each tile is filled in order on a list.
        #   --> Do I need to worry about synchronizing flow across multiple frames?
        content_heights = {
            'heading': self.children['heading'].content_size.height,
            'spacer': self.children['spacer'].content_size.height,
            'body': self.children['body'].content_size.height,
        }
        content_height = sum(content_heights.values())
        # don't do this:
        #   content_width = max(self.content['heading'].content_size.width, self.content['body'].content_size.width)
        # because all that sizing effort will have been done already in the measure method.
        content_width = target_extent.width
        content_region = Region(
            Pos(Distance.zero, target_extent.height - content_height),
            Extent(content_width, content_height)
        )

        # Stack all the child text vertically
        # We don't want to pass on to their layout methods b/c they will apply an anchor which is subsumed by the paragraph style.
        self.regions = {
            child_name: Region(
                Pos(Distance.zero, content_height - cumulative_height),
                Extent(content_width, child_height)
            )
            for (child_name, child_height), cumulative_height
            in zip(content_heights.items(), itertools.accumulate(content_heights.values()))
        }
        # I need inheritable unit converters - so I can propagate them outwards to Pos, Extent and Region.
        logging.info("new layout %s", content_region.logstr())
        return content_region

    def draw(self, c: DisplaySurface, region: Region):
        """
        Render the Kanji summary text in the passed coordinate space.

        The region passed into draw() _should_ be region computed by do_layout() but
        there is no guarantee that that's true.

        :param c: a surface that knows how to execute the drawing commands that we send to it.
        :param region: a coordinate space for drawing independent of surrounding elements.
        """
        self._state = States.drawn | States.all_data_consumed

        if not any((child_content.text for child_content in self.children.values())):  # type: ignore
            return

        origin = region.origin
        logging.info("drawing in %s", region.logstr())
        for (child_name, child_element), child_region in zip(self.children.items(), self.regions.values()):
            logging.info("drawing child element '%s' in %s", child_name, child_region.logstr())
            child_element.draw(c, child_region + origin)
        return
