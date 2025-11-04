.. kanji_summary.py.dev_notes:

==================================
kanji_summary.py Development Notes
==================================

For: :mod:`reports.kanji_summary.kanji_summary.py`

.. include:: /common

Future Feature Adds
-------------------

Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - ReportLab handles text overflow - what doesn't fit in the output rectantle gets saved for the next output call.

        - we'll need to handle this situation ourselves in the general flowing output case.
        - this strongly ties into pagination strategies

Data
~~~~
    - Hiragana + Katagana: KanjiSVG has drawings for these characters but I have no backing data store to tell a story about them

        - Wiktionary seems to have a lot of information about the other kana - I've experimented with some REST queries to extract it
        - Presenting these data may need a variant on the KanjiReport unless I can shoehorn the input into the right spots on a
          `KanjiReportData` instance.

Layouts
~~~~~~~

    - Should there be some kind of synchronization tactic for coordinating flowing output in several frames in the same container?

        - Maybe certain markers that have to align horizontally or vertically across frames?
        - Beware of getting too "meta" on this and making uber-layout strategies controlling layout strategies.

    - Review: Is it worth creating a "text layout" that understands flowable content better than the stacking strategy?

        - Does this even make an interesting split of strategies into "flowing & wrapping" vs "fixed dimensions"?
        - How deep would the split go:  frames? containers? layout strategies?

Data Forwarding
~~~~~~~~~~~~~~~

    - This is an architectural feature, not an app feature.
    - Property getter/setter functions don't have to operate on :python:`self` - you could operate on a delegatee target instead.
    - Consider an :python:`@delegated_property(target)` decorator that works like :python:`@property`. A companion `@delegated_setter` too?
    - This would considerably clean up delegatee data handling in the `DelegatingRenderingFrame` mixin and make :python:`Protocol`
      delegation smarter.

    - On a different use case, it would be convenient to seemlessly (i.e. without developer action) propogate unit properties
      on the `Distance` type (or any other type) outwards to types that aggregate `Distance` instances (such as `Extent`, `Pos`, `Region`)

      - I'm thinking that somthing like :python:`extent.in` yields a namedtuple (or anonymous :python:`tuple`?) of floats with :python:`.width` and :python:`.height` in inches.
        The property :python:`in` propogates upwards from the `Distance` instances in the `Extent` instance.
      - This may require a completely different mechanism from the :python:`@delegated` decorators.
      - Since I'm such a big fan of decorators, maybe :python:`@units(dimension)` -- see the `Distance` dev notes.

    - What about layout math? See notes on `Container.measure`.

        - Consider:  is "percent of X" where X is property live-delegated to some other `Distance` instance?
        - Of course, data forwarding and delegates in this use case also raises the spectre of change notification & when are they necessary.

Whitespace Handling
~~~~~~~~~~~~~~~~~~~

    - There's a lot of notes about removing whitespace consideration from measure.

        - I'm no longer convinced that this is a correct tactic.
        - The two frame styles of flowing and fixed boundaries handle whitespace somewhat differently
        - There should be a tight coupling to the intended _simple_ `Distance` constraint mechanism and whitespace allocation.

    - measure() should certainly be returning an _minimum_ size necessary but it could include the host frame's own internal
      whitespace management.
    - whatever the outcome on this issue, it strongly affects the semantics of the size properties of `RenderingFrame` such as
      `requested_size` et al.

Code Review/Adjustments
-----------------------

    - Factor: replace most of kanji_summary.kanji_summary.KanjiSummary with `EmptySpace` frames to do padding and put
      all of the child text into `FormattedText` frames all wrapped in a vertically stacked `Container` frame.
    - Review: the parent `SimpleElement` class owns the `_requested_size` data. Touching this private parent data during
      `KanjiSummary.__init__` is a faux pas. Consider a forwarding property whose setting passes the data up to the parent.
      See the notes about aliasing and forwarding for `DelegatingRenderingFrame`.
    - Factor: put attribute attrgetters onto the geometry classes to replace the ones in `KanjiSummary.measure` for FP convenience
    - Factor: use my coalesce helpers for distance instead of 'or None'
    - Doc: is the `sd_infosheet_dynamic_layout` Mermaid diagram in :python:`kanji_summary.report.Report` in the wrong spot?
      Generalize it and put that with `PaginatedReport`?
    - Doc: the `fc_infosheet_generate` Mermaid diagram in :python:`kanji_summary.report.generate` is also releveant to `PaginatedReport`.
      Move it or copy a generalized version.
    - Review: :python:`kanji_summary.report.Report.get_page_layout` is not very robust - needs a review of the possible failure
      modes and appropriate error handling.

        - Same story for :python:`kanji_summary.report.generate` - what about unrecognized kanji input (ie a "no data" case)?

    - Review: a nice-to-have is multiple kanji in one report with practice sheets interleaved.
      See the dev note about the "Report chaining" features - seems a logical place to do this.





