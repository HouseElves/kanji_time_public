:orphan:

.. _distance.py.dev_notes:

=============================
distance.py Development Notes
=============================

For: :mod:`visual.frame.distance`

.. include:: /common

Future Feature Adds
-------------------

Enhanced `Distance` features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - The :python:`layout.Distance` constaint model is primitive
    - I'm not entirely happy with "stretchyness" tied to a unit.
      I'm thrilled with it conceptually, but I'm not sure about how I feel about how I've implemented it.
    - `RenderingFrame.measure`, `RenderingFrame.do_layout` and `RenderingFrame.draw` are always the intended `Distance` clients.
      These methods drive constraint and other new `Distance` features.  Review the code in existing implementations.
    - the minimum constraint case is going to be at_least, at_most, and between.  However I go, I need to ensure consistent semantics.

        - maybe move away from fixed flags and define a distinct `Constraint` type?
        - this gets to an "apply constraints" semantic that adjusts a distance or a "satisfies constraints" that checks.
        - raises the possibility of constraint expressions linked with logical connectives.
        - who owns a constraint?  Maybe it should be decoupled from the `Distance` type.
        - how do constraints interact with equivalence? Consider a case for "at least 5" equal to anything bigger or equal to 5.
          This case sounds more like a "matches" semantic, not an "equivalence" semantic.

    - `Distance` dependencies couild be useful too.

        - This is already a necessity to implement percentages on proportional layouts
        - Dependencies also naturally arise with my new property delegation model
        - Does this generalize to more expressions?  I.e width = 1.62*height -- but I manage the height value during layout and
          propogate it through its dependers by invalidating completed layouts?  `measure` would have to create a top-sorted recalc chain
          as a side effect to pass through/available to `do_layout`.
        - Eeek! a gradient descent optimization during layout... the mind boggles... let Torch deal with the details - too fancy but an
          interesting thought.

    - Outward propagation of the "unit" properties to types that contain them?  From the Data Forwarding notes on "kanji_summary.py":

        - It would be convenient (at least for debugging) to seemlessly propogate unit properties on the `Distance` type (or any other type)
          outwards to types that aggregate `Distance` instances (such as `Extent`, `Pos`, `Region`)
        - Something like :python:`extent.in` yields a tuple of floats with :python:`extent.width` and :python:`extent.height` in inches.
          The property :python:`in` propogates upwards from the `Distance` instances in the `Extent` instance.
        - This will require the help of the new property delegation and data forwarding featrues.

    - Much longer term vision:

        - a Measurement protocol with L/T/M dimensions [or even $ and counting categries], fuzzy/crisp aspects and arithmetic.
        - the Measurement owns its own units, conversion tables, and parser just like Distance does
        - create Measurements on-the-fly for products and quotients like "Newton-metres" or "metres/second".
        - maybe even expose some common constants on specific well-known measures.



Code Review/Adjustments
-----------------------

    - Review: check usage of :python:`layout.distance.DistanceUnit` - am I dupliating work already in enum.StrEnum?

        - particularly with the :python:`layout.distance.unit_str` dictionary

    - Factor: :python:`Distance.MeasureType` needs to support ConvertibleToFloat if it doesn't already
    - Factor: should :python:`Distance.MeasureType` be a Generic type parameter?
    - Factor: make :python:`Distance.fit_to`, :python:`Distance.zero`, and :python:`Distance.infinite` into immutable `Singleton` instances.
    - Review: `Distance` should have a property for it's default __str__ (et al) format - sig figs, fraction, digits etc.  How does numpy do this?

        - it strikes me that I should able to do this an overridable style in the new Styles model.

    - Factor: pull out the magic distance value regexp from :python:`Distance.parse` to a class property.
    - Review: stretchy (unit == '*') handling in :python:`Distance.__lt__` et al looks sketchy/incomplete.
    - Review: is the Numeric library any use to me for distances and :python:`Distance.MeasureType`?
      `numeric` has always been unpleasant to use because it's so poorly typed, but maybe I'll get lucky here.
    - Factor: can I unify the code in :python:`Distance.__eq__` and :python:`Distance.__lt__` w.r.t their match strategy?

