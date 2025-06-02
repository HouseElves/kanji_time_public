.. _formatted_text.py.dev_notes:

===================================
formatted_text.py Development Notes
===================================

For: :mod:`visual.frame.formatted_text`

.. include:: /common

Future Feature Adds
-------------------

Formalize Simple HTML text markup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Just like it says on the tin:  I need to specify Simple HTML formally for compliance testing.
    - Extract from ReportLab, tweak, and create a DTD for it.

        - Why go with XML when I hate XML? The DTD |rarr| RDBMS schema project.
          I'd love to be able to suck text into a database on my terms and XML approach enhances the yield of my IP.
        - I'd end up with semantic label tags on structural document elements.

    - Maybe RST would make for a better home technology for formatted text?  Explore the trade-offs.


Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Decouple the ReportLab implementation from the simple HTML text in :python:`visual.frame.formatted_text.FormattedText`.

        - As in the `Drawing`, I don't really want to create domain-specific languages for every type of rendering frame.
          ReportLab's simple HTML-like XML for text markup seems like a great starting point for a home technology
        - Using the Simple HTML as a home technology suggests as well different adapters for markdown or DocBook.
          I don't want to reinvent PanDoc! So let's keep this simple.

Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - :python:`FormattedText.getSpace{After|Before}` should be part of a `PaddingService` mix-in?

        - not part of a whitespace strategy b/c these are static constraints to a frame
        - concept for a `PaddingService` is a standard set of properties that supply constraints to a strategy

Code Review/Adjustments
-----------------------

    - Factor: decouple the formatted text content from the ReportLab rendering technology
    - Factor: figure out a way to remove :python:`frame.FormattedText.height_extra` to a global "rounding pad" in settings.
      Does this padding belong more appropriately in the geometry?
    - Review: `FormattedText.measure` has another use case for baked-in constraints on the Distance type.
    - Review: the semantics around passing the extent to :python:`RenderingFrame.measure` seem inconsistent.

        - look more closely at how extent is used in the `measure` methods in `FormattedText`, `Drawing`, `Container`, and `SimpleElement`.

    - Factor: casting Sequence[Flowable] to list[Flowable] in :python:`FormattedText.draw` speaks to a lack of design planning.
      correct the underlying types.
