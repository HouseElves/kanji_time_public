.. _stack_layout.py.dev_notes:

=================================
stack_layout.py Development Notes
=================================

For: :mod:`visual.frame.stack_layout`

.. include:: /common

Linter Complaints
-----------------

    - :python:`external_data.kanji_svg` has several refactoring complaints from PyLint.

Future Feature Adds
-------------------

Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - does a layout strategy own a whitespace strategy or does this come in on the measure/layout calls as a parameter?

        - Regardless, I'm going to need some kind of default whitespace handling in all of the `LayoutStrategy` instances if a whitespace
          strategy is not provided for :python:`LayoutStrategy.measure` or :python:`LayoutStrategy.layout`.
        - Maybe create a default strategy that gets initialized with some minimum inter-frame padding does the even-distibution thing like
          I'm doing now:  this would be an easy first step to have a look at what this Whitespace strategy architecture would imply.

Code Review/Adjustments
-----------------------

    - Nomenclature: are :python:`StackLayoutStrategy.get_stack_pos` & :python:`StackLayoutStrategy.get_other_pos misnamed`?
      Use `get_{stack|other}_idx` instead?
    - Review: do I need options to the `StackLayoutStrategy` initializer for inter-element spacing?
    - Review: is it appropriate to throw a `RegionOverflow` exception up to :python:`StackLayoutStrategy.layout`'s caller?
      It seems icky to me to misuse an exception on a normal execution case that could be handled by a boolean "clip" setting in the
      `LayoutStrategy` protocol.  OTOH, Python idiom encourages this approach.  Hybrid?  When no "clip" setting, raise an exception?
      There's peril there: don't over-complicate the interface with implicit behaviors.
    - Review: note that whenever content isn't clipped by `layout`, I'll be getting an implict z-order imposed by the order in which I draw
      the frames where later ones overwrite earlier ones; which could raise some interesting apparent bugs on output consistency.
    - Factor: horizontal/vertical helper methods + associated direction enum should be exposed as a mix-in so anybody can use them
    - Review: :python:`StackLayoutStrategy.layout` has explicit coordinate system assumptions about origin placement and axis direction
    - Review: is disregarding frames with any zero dimensions in :python:`StackLayoutStrategy.layout` appropriate? What are the unintended
      consequences of doing this?

