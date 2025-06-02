"""
Model various page rules as content frames.

.. only:: dev_notes

    - Doc guidelines - documentation style rules about what properties go into the Mermaid class diagram:  just @property or all self data?

        - my thoughts are "as appropriate" to the diagram.

----

.. seealso:: :doc:`dev_notes/page_rule_notes`

----

"""

from visual.frame.simple_element import SimpleElement
from visual.layout.region import Extent, Region
from visual.protocol.content import DisplaySurface, States


class HorizontalRule(SimpleElement):
    """
    Represent a horizontal page rule.

    Initialize a page rule with the following.

    :param size: the length of the rule - this is really "requested_size", make consistent nomenclature.
    :param color: the fill color for the rule.


    .. only:: dev_notes

        - vertical rules, too.  Best to parameterize the class instantiation.
        - to be considered a "rule" we must span the entire width of the parent container.
          Arguably, a page rule should be considered a part of the layout strategy or a container attribute ("add rule separators" N/S/E/W?).
          In this scenario, this class becomes a "line" element?  Maybe?

    Class Relationships
    -------------------

    An page rule has simple direct class relationships: it only interacts with the SimpleElement base class and the ReportLab drawing
    primitives on the display surface.

    .. mermaid::
        :name: cd_rule
        :caption: Class relationships for a page rule section separator.

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
            SimpleElement <|-- HorizontalRule

            class HorizontalRule {
                <<realization>>
                +Extent size
                +ReportLab.Color color
                +measure(self, Extent extent) Extent
                +draw(self, DisplaySurface c, Region region)
            }

    """

    def __init__(self, size, color):
        """Initialize a horizontal page rule with a width and a color."""
        super().__init__(size)
        self.content_size = size
        self.color = color

    def measure(self, _extent: Extent) -> Extent:  # type: ignore
        """
        Measure the minimum size of the page rule.

        :param extent: the estimated space allocated to the page rule element in the final layout.

        :return: the amount of space required for the page rule element.

        .. only:: dev_notes

            - Why do I need to implement this?  It's ignored.  Let SimpleElement handle it.
              Unless SimpleElement is doing something naughty?  Review.

        """
        return super().measure(self.content_size)

    def draw(self, c: DisplaySurface, region: Region):
        """
        Render the page rule at the requested location.

        The draw operation is ReportLab-specific - it uses PDF Canvas drawing primitives on the display surface to draw the rule.

        :param c: a ReportLab PDF canvas drawing surface
        :param region: offset + extent into the display surface for the empty space

        :return: None
        """
        (rule_x, rule_y), (rule_width, rule_height) = region
        assert self.content_size is not None
        c.setLineWidth(self.content_size.height.pt)
        c.setStrokeColor(self.color)
        c.line(rule_x.pt, rule_y.pt + rule_height.pt//2, rule_x.pt + rule_width.pt, rule_y.pt - rule_height.pt//2)
        self._state = States.drawn | States.reusable
