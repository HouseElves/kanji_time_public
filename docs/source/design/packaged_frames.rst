.. _builtin_frames:

================================================
What Rendering Frames are built into Kanji Time?
================================================

.. _ReportLab: https://pypi.org/project/reportlab/

Kanji Time provides 6 simple implementations for the :class:`RenderingFrame` protocol that model common use cases or demonstrate solving common layout problems as follows.

    Atomic Frames
        Frames that contain a single type content to be rendered inside one rectangle: ReportLabDrawing, FormattedText, HorizontalRule, and EmptySpace.

    SimpleElement Base Frame
        The SimpleElement is a default do-nothing implementation of :class:`RenderingFrame` suitable for deriving custom atomic frames or custom container frames.

    Container Frame
        The Container is a simple-as-possible implementation of a rendering frame that holds other rendering frames and lays them out using a LayoutStrategy instance.

One of the interesting issues that came up while designing the layout interface is the difference in handling flowing vs fixed size content.

Content such as text *flows* across its bounding box, wrapping to a new line when it hits a boundary.
It also flows down its bounding box until it hits the bottom where it needs a new bounding box on a new page.

Content such as a diagram is *fixed* in that it either fits in its bounding box or it doesn't.
Vector graphics may be scaled to fit the drawing it the available space or we could split the drawing across multiple bounding boxes on different pages.

These considerations were in large part responsible for driving the design decision to leave pagination up to the individual rendering frames on a page.

The measurement algorithms are good but there's still some vestigial issues to be resolved in the next development cycle.

.. rubric:: Layout Model Contents
    :heading-level: 2

.. rubric:: Atomic Frames
    :heading-level: 3

- :ref:`rl_drawing`
- :ref:`rl_text`
- :ref:`es`
- :ref:`hrule`

.. rubric:: Frame Base Classes
    :heading-level: 3

- :ref:`simple`
- :ref:`cont`

.. rubric:: Custom Frames
    :heading-level: 3

- :ref:`custom`

.. seealso::

    - :ref:`layout ideas <layout_and_geometry>` for raw notes about future adjustments to layout
    - :ref:`sizing protocol changes <layout_and_geometry>` and :ref:`Distance type enhancements <layout_and_geometry>` for raw notes about future adjustments to :attr:`RenderingFrame.requested_size` and its ilk.

----

.. _atomic_frames:

Built-in Atomic Frames
----------------------

.. _rl_drawing:

ReportLabDrawing
~~~~~~~~~~~~~~~~

A :class:`ReportLabDrawing` frame contains a scalable vector graphic formatted for use in ReportLab_ documents.
There is no attempt to paginate or fit drawings into their bounding box at this time.

There is planned work to decouple this rendering frame from the ReportLab_ technology.

.. seealso::

    See :ref:`new rendering abstractions <rendering_technology>` for raw notes about creating a pluggable technology layer underneath the Kanji Time layout model.

Back to :ref:`builtin_frames`

----

.. _rl_text:

FormattedText
~~~~~~~~~~~~~

A :class:`FormattedText` frame contains a block of text possibly marked up with a simplifed HTML-like set of tags for formatting.
FormattedText instances consume their bound data as it rendered on each page, thus simplifying the pagination process.
There is also an initialization flag to suppress this behavior for static text to be presented on all pages.

The simplified HTML language for formatting is inherited from ReportLab_.
There is planned work to decouple from ReportLab_ in the next development cycle.

.. seealso::

    See :ref:`new rendering abstractions <rendering_technology>` for raw notes about creating a pluggable technology layer underneath the Kanji Time layout model.

Back to :ref:`builtin_frames`

----

.. _es:

EmptySpace
~~~~~~~~~~

A :class:`EmptySpace` frame is exactly what it says on the tin.

Use one of these frames to reserve an area on the page as blank space.
Use :class:`EmptySpace` instances with care and fore-knowledge of the layout strategy's behavior because you don't have direct control over
where the empty space will be placed.

Back to :ref:`builtin_frames`

----

.. _hrule:

HorizontalRule
~~~~~~~~~~~~~~

A :class:`HorizontalRule` frame contains a horizontal seperator line flowing across the full width of its bounding box.

The Kanji Summary report uses a :class:`HorizontalRule` instance to separate the banner section from the dictionary defintion content section.

There is no vertical version of a page rule at this time.
There is planned work to do so -- and there are also some design issues to resolve around the best owner for a page rule.

.. seealso:: The :ref:`layout ideas <layout_and_geometry>` contain some raw notes about future handling of page rules.

Back to :ref:`builtin_frames`

----

Frame Base Classes
------------------

.. _simple:

SimpleElemement
~~~~~~~~~~~~~~~

** work in progress **

Back to :ref:`builtin_frames`

----

.. _cont:

Container
---------

** work in progress **

Back to :ref:`builtin_frames`

----

Custom Frames
-------------

.. _custom:

Custom Frame Demo Code
~~~~~~~~~~~~~~~~~~~~~~

The Kanji Summary report contains some vestigial custom frames derived from :class:`SimpleElement` that act as containers for the kanji readings and the kanji radical summary; namely

    - :class:`KanjiSummary`, and
    - :class:`RadicalSummary`.

I've left these two classes as-is instead of converting them to a generic :class:`Container` as demonstration code for creating a custom container frame.
They are a little rough around edges representing early work in the project.

Back to :ref:`builtin_frames`

