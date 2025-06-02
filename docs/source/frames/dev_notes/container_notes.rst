.. _container.py.dev_notes:

==============================
container.py Development Notes
==============================

For: :mod:`visual.frame.container`

.. include:: /common

Thread Safety (for a multithreaded future)
------------------------------------------

    - Explicitly setting state in any of the `RenderingFrame` implementations looks sketchy for multiple threads, especially
      :python:`visual.frame.Container` and :python:`visual.frame.SimpleElement`.

        - Have a good look at some of the concepts in :python:`visual.frame.protocol.content.States` for more robust management of state
          transitions via a context manager + associated formal goo.

Linter Complaints
-----------------

    - evaluate :python:`StackLayoutStrategy.layout` for factoring - pylint is complaining about too-many-locals

Future Feature Adds
-------------------

Layouts
~~~~~~~

    - Add support for floating child containers & a z-axis one day to the :python:`visual.frame.Container` one day.

        - Floating frames should manifest as a *strategy* (i.e. a :python:`visual.protocol.layout_strategy.LayoutStrategy` instance) not
          as a Container specialization! _Prefer aggregation over inheritance._
        - But... there may be assumptions in `Container` that will be violated if we introduce a z-axis. Review carefully!

    - I have defined a :python:`RenderingFrame.resize` capability but I'm not using it.

        - It's time to decide if this method should stay or go.
        - A decision either way affects :python:`visual.frame.Container` and :python:`visual.frame.SimpleElement` and the pagination loop.

Styles
~~~~~~

    - Use the new style application mechanism for drawing debug frame rectangles.


Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - The anchor point semantic isn't really well defined in `Container` vs `RenderingFrame` instances.  See :python:`Container.do_layout`.
    - The :python:`frame.SimpleElement` class has a note about maybe passing an anchorpoint to :python:`RenderingFrame.do_layout` to position
      the layout in the extent?

        - I am suspicious of adding an anchorpoint parameter to :python:`RenderingFrame.do_layout` because it adds more nuance to the `extent`
          parameter -- which is already semantically ambiguous.
        - Consider how `Distance` constraints can lift the semantic ambiguity by baking intention into the `extent` parameter.

    - The "evenly distributed" algorithm for whitespace allocation in :python:`Container.measure` is the canonical use case for having
      whitespace allocator strategy types.
    - :python:`Container.do_layout` has a note that "We don't care about inter-element gaps - the frame is responsible for its own explicit margins."
      How does this fit into any changes or consistency-normalization in whitespace handling?


Code Review/Adjustments
-----------------------

    - Factor: PRIORITY - remove the `update` method from the :python:`visual.frame.container` - this is an ugly hack and the use case for it is
      no longer relevant.
    - Review: how does an AnchorPoint interact with a Container.
    - Review: consider "Partially Reusable" as a container sub-state of reusable?  is this worth the effort? or meaningful?
    - Factor: how do child frames and the Container handle a begin_page request? This is a little wishy-washy.

        - Who handles passing the `begin_page` message along?
        - Is recursing through the child frame tree a good idea?
        - Commit one way or another in :python:`Container.begin_page`

    - Review: is the two-pass child measurement algorithm in :python:`Container.measure` really the right way to go?
    - Review: take a critical look at the share-evenly strategy for whitespace in :python:`Container.measure`.
    - Review: the "deferred measure" case for stretchy dimensions in :python:`Container.measure` isn't very robust.
      It works now, but this is a bug farm waiting to happen not just with unhandled failure modes but also with sub-awesome algorithm design.

        - There's no hard limits on space allocation
        - There's no overflow checking
        - There's no "negotiation" with children to squeeze frames together
        - :python:`Container.measure` is the canonical use case for baking a more robust constriant mechanism into the `Distance` type.
          See the development notes for `Distance` for more details.
        - Things go wonky when any part of an extent goes negative or even falls below a minimum content threshold
        - Would handling page-overflows via an exception make sense? Is it Python idiomatic?

    - Factor: allowing Extent instances to be polymorphic through non-geometry types seems sketchy.
      See the intractions between :python:`Container.measure` and :python:`Container.do_layout` and :python:`LayoutStrategy.measure`.
      I am sub-enthused.
    - Review: do I need to anchor a child in the parent, which affects my computed origin, or myself?





