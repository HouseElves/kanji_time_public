:orphan:

.. _content.py.dev_notes:

============================
content.py Development Notes
============================

For: :mod:`visual.protocol.content`

.. include:: /common

New Features
------------

Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - :python:`visual.protocol.content.DisplaySurface` needs to be a generic protocol for a technology,
      not explicty bound to :python:`ReportLab.canvas.Canvas`


Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - Consider adding a `redistribute_whitespace` method to the `RenderingFrame` protocol.

        - This implies an idea of `fixed` vs `variable` portions of layout within a frame.
        - Certain minimum whitespace padding would get incorporated into the `fixed` size.
        - Can I accomplish this just by redoing `do_layout` or are there some assumptions that I bake into `redistribute_whitespace` to make
          it less weighty?  One of these would clearly be about `fixed` sizes.

State labels/transition Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - I actively dislike having explict state labels out of an enum.
      They have a nasty habit if getting out of synch with the actual set of data values that they describe.
    - Consider the notes on `visual.protocol.content.States` about how to keep synchnonization.
    - Define a mix-in for explicity state transition behavior with:

        - `in_state` method that maps instance data to a state-enum value rather than just reading a cached state-enum.
        - `check_state` method that confirms the instance data conforms to a state-enum value or set of values.   __contains__ would be awesome for the **in** keyword.
        - `ready_for` method that checks if the instance can make a transition from its current state to some new one.

    - have a context manager "with doing_transition_to(States.some_state):" that has smarts to

        - verify that the object is a state that _can_ move to the target state
        - manage rollback should the transition fail and/or raise appropriate errors
        - handle thread safety issues

Code Review/Adjustments
-----------------------

    - Review: other properties on `RenderingFrame` such as "clipable"?
    - Review: why am I not using :python:`utilities.general.coalesce_None` and its ilk to fill in missing values?
      Doesn't Extent have a `coalesce` classmethod?
    - Review: the `RenderingFrame` protocol is pretty bossy about how much data that it wants.
    - Review: several notes removed from :python:`RenderingFrame.measure` method are addressed below

        **Q**: should I  be returning a width/height range and a function relating max_width |rarr| min_height and max_height |rarr| min_width?

        **A**: this idea was addressing flowables where height is a function of width - it's been subsumed with better layout logic.

        **Q**: why do I even have to pass and return an Extent?

        **A**: the passed extent is the maximum space for the frame on a page. We return a minumum space required within that passed Extent.

        **Q**: how about a "requires remeasure" for dimension changes?

        **A**: this will be addressed in a `Distance` dependency model external to the frame.

