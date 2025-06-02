"""
Model a block of text represented in a ReportLab paragraph set.

.. only:: dev_notes

    - Decouple the formatted text content from the ReportLab rendering technology.
    - Consider the home technology for a FormattedText frame.

         - ReportLab's paragraphs are really a simplified HTML that would be useful in general.
         - Maybe take the XML as input and derive a ReportLab version of this container?

----

.. seealso:: :doc:`dev_notes/formatted_text_notes`

----

"""

# pylint: disable=fixme

from collections.abc import Sequence
import logging
from typing import cast

from reportlab.platypus import Paragraph, Frame, Flowable

from visual.frame.simple_element import SimpleElement
from visual.layout.anchor_point import AnchorPoint
from visual.layout.distance import Distance
from visual.layout.region import Region, Extent
from visual.protocol.content import DisplaySurface, States


logger = logging.getLogger(__name__)


class FormattedText(SimpleElement):
    """
    A container for text contained a sequence of ReportLab paragraphs that may include formatting.

    Text is interesting in that unlike other framed elements, it *wraps*.
    Text wants to fill up all the available width before starting a new line, which makes the text element's height a function of its width.
    ReportLab calls this "Flowable" content.

    A direct consequence of wrapping is that every time a layout strategy changes the available size for our text, we need to remeasure.

    Text is allowed to span multiple pages - a FormattedText instance will automatically consume the text that it output to its draw region
    after a successful draw operation; and then scroll forward to the beginning of the next chunk.
    The owner of a FormattedText can disable this to do its own page management or keep a constant text content by sending True on
    "do_not_consume" at initialization.

    Initialize a FormattedText instance with the following.

    :param requested_size: amount of space to reserve for the frame content
    :param anchor: rough location in the owning frame
    :param text: marked up content text
    :param do_not_consume: pass True to carry the same text content onto the next page

    FormattedText has simple direct class relationships: it only interacts with the SimpleElement base class and the ReportLab text element
    implementation as a sequence of "Flowable" instances.

    .. mermaid::
        :name: cd_formatted_text
        :caption: Class relationships for a simple HTML-like text frame.

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
            SimpleElement <|-- FormattedText

            class FormattedText {
                <<realization>>
                +getSpaceBefore() : float
                +getSpaceAfter() : float
                +measure(Extent extent) Extent
                +draw(DisplaySurface c, Region region)
            }
            FormattedText : AnchorPoint anchor
            FormattedText : Extent content_size
            FormattedText : bool do_not_consume
            FormattedText --o "n" Flowable : text
     """
    height_extra = 1.0  # this is a rounding pad.  it should be optional as  a property

    def __init__(self, requested_size: Extent, anchor: AnchorPoint, text: Sequence[Paragraph], do_not_consume=False):
        """Initialize the content with a dummy SVG and the dummy text."""
        super().__init__(requested_size)
        self.anchor = anchor
        self.text: Sequence[Flowable] = text
        self.content_size = Extent.zero
        self.do_not_consume = do_not_consume

    def __bool__(self) -> bool:
        """Produce true when this rendering frame has non-trivial content."""
        return bool(self.text)

    def measure(self, extent: Extent) -> Extent:
        """
        Measure the minimum size of the element.

        Text is interesting because its height varies with its width.
        When the extent is absent, we'll try to compute a sensible default text size.

        The actual text height is the height of each paragraph + the inter-paragraph spacing before and after.
        Of course, "after" spacing doesn't apply the last paragraph and "before" spacing doesn't apply to the first.

        We'll expose these spacings on getSpace{After|Before} properties.

        :param extent: the maximum space we can allocate to this element.

        :return: the minimum size that we need for the text --> a/k/a the content size.

        .. only:: dev_notes

            - getSpace{After|Before} should be part of a PaddingService mix-in
            - some state caching so I don't have to repeatedly call out to ReportLab to measure text extents
            - try to leverage baked-in constraints with a Distance type

        """
        self._state = States.needs_layout

        if not extent:
            # Force zero on both axes
            extent = Extent.zero
        # revised this.
        # minimum_size = self.requested_size | extent  # | => Extent union operator
        assert extent is not None
        minimum_size = Extent(
            # try to leverage baked-in constraints with a Distance type. `at_most` is applicable here on requested size.
            max(self.requested_size.width, extent.width),   # we're fitting to width, so we need as much space as offered.
            min(self.requested_size.height, extent.height)  # don't want to overflow unless we measure it so explicitly
        )
        if not self.text:
            self.content_size = Extent.zero
            return self.requested_size | extent  # revised from minimum_size

        text_width = max(
            Distance(max(text.minWidth() for text in self.text), "pt", at_least=True),  # type: ignore
            minimum_size.width
        )
        text_height = minimum_size.height

        # Get the height of each paragraph and the inter-paragraph spacing.
        # Paragraph.wrap() seems to ignore the passed height
        text_height_float = sum(text.wrap(float(text_width.pt), float(text_height.pt))[1] for text in self.text)
        text_after_float = sum(text.getSpaceAfter() for text in self.text[:-1])
        text_before_float = sum(text.getSpaceBefore() for text in self.text[1:])

        # save the total text height to position the origin in our draw region
        total_text_height = Distance(
            text_height_float + text_after_float + text_before_float + self.height_extra, "pt",   # type: ignore
            at_least=True
        )
        self.content_size = Extent(text_width, total_text_height)

        # Now return the union of the computed size and the minimum size.
        # Review -> why do I need the passed extent??
        return super().measure(self.requested_size | self.content_size)  # removed:  | extent # revised from minimum_size | self.text_extent

    def getSpaceBefore(self) -> float:  # pylint: disable=invalid-name
        """Provide ReportLab Flowable attribute for space before my paragraphs-as-a-unit."""
        return self.text[0].getSpaceBefore() if self.text else 0

    def getSpaceAfter(self) -> float:  # pylint: disable=invalid-name
        """Provide ReportLab Flowable attribute for space after my paragraphs-as-a-unit."""
        return self.text[-1].getSpaceBefore() if self.text else 0

    def do_layout(self, target_extent: Extent) -> Region:
        """
        Position all visible elements inside the passed extent.

        :param target_extent: - amount of space available to my text content.

        :return: an offset + extent into the target_extent (as a Region) that identifies where to draw the text content.
        """
        self._state = States.ready

        if self.content_size not in target_extent:
            logger.warning("Not enough space to render all text.  Trimming")
            self.content_size = self.content_size & target_extent
            # raise ValueError("Expected enough space to draw the text!")
        origin = self.content_size.anchor_at(self.anchor, target_extent)
        return Region(origin, self.content_size)

    def draw(self, c: DisplaySurface, region: Region) -> None:
        """
        Render the formatted text in the requested region.

        *IMPORTANT*

        The ReportLab frame must be initialized with zero padding!
        We do all our own layout.

        :param c: a ReportLab PDF canvas drawing surface
        :param region: offset + extent into the display surface for the text content.

        :return: None

        .. caution:: Use Frame.addFromList with care!
           It will remove all rendered content from the passed list of ReportLab Flowables.
           This mutation is very useful for on-the-fly pagination, but a nasty surprise if you're not expecting the behavior.

        A summary of how the different players interact to for paginating text is in the below sequence diagram.

        .. mermaid::
            :name: sd_formatted_text_draw
            :caption: Sequence diagram for paginating data that overflows its page frame.

            sequenceDiagram
                participant Controller
                participant Page
                participant FT as FormattedText

                Controller->>Page: add(FormattedText)
                Controller->>Page: measure()
                Page->>FT: measure(extent)
                Controller->>Page: draw()
                Page->>FT: draw(canvas, region)
                FT->>FT: mutate text[] (if not do_not_consume)
                FT-->>Page: set state (drawn + have_more_data or all_data_consumed)

        At high level, the pagination state is tracked in the RenderingFrame.State property implemented in _state as in this
        transition diagram.

        .. mermaid::
            :name: st_formatted_text_draw
            :caption: State transitions for paginating data that overflows its page frame.

            stateDiagram-v2
                [*] --> needs_layout
                needs_layout --> ready: do_layout()
                ready --> drawn: draw()
                drawn --> reusable: if do_not_consume
                drawn --> have_more_data: if drawlist not empty
                drawn --> all_data_consumed: if drawlist empty

        .. only:: dev_notes

            - casting Sequence[Flowable] to list[Flowable] speaks to a lack of design planning.  Review assigned types.

        """
        state = States.all_data_consumed
        (content_x, content_y), (content_width, content_height) = region.origin, region.extent
        text_frame = Frame(
            content_x.pt, content_y.pt, content_width.pt, content_height.pt,
            topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0,
            showBoundary=0
        )
        logging.info("rendering\n\t%s", "\n\t".join(cast(Paragraph, t).getPlainText() for t in self.text))
        drawlist = cast(list[Flowable], self.text)  # casts from Sequence to list - correct the types at the source.
        if self.do_not_consume:
            drawlist = list(drawlist)
        text_frame.addFromList(drawlist, c)
        if drawlist:
            logging.warning("NOT rendered\n\t%s", "\n\t".join(cast(Paragraph, t).getPlainText() for t in drawlist))
            # use the remaining drawlist for the next page if we've got one.
            state = States.have_more_data
        if self.do_not_consume:
            assert not drawlist, "Cannot spill over pages when retaining text content."
            state |= States.reusable
        self._state = States.drawn | state
