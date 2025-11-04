.. _empty_space.py.dev_notes:

================================
empty_space.py Development Notes
================================

For: :mod:`visual.frame.empty_space`

.. include:: /common

Code Review/Adjustments
-----------------------

    - Review: consider some kind of text client services mixin to get rid of the "text" property on :python:`frame.EmptySpace`.
      That property only exists to allow me to inject empty spaces into a sequence of `FormattedText` instances without having to special case
      the processing loop. Abstracting this expediency to a mixin would make it "intentional design" instead of "an ugly hack".

        - Suggests that a RenderingFrame implementation could expose a do-nothing "Impersonator" mixin.
          :python:`EmptyTextSpace(EmptySpace, FormattedText.Impersonator)` (check ordering!)
        - This is an interesting concept for blending capabilities. Worth exploring.

    - Nomenclature: The :python:`frame.EmptySpace` initializer should  have requested_size parameter, not size, for consistency.
    - Factor: can I remove :python:`frame.EmptySpace.draw` and let the `SimpleElement` base class handle it? That's its job.

