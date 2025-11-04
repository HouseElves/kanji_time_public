.. _drawing.py.dev_notes:

============================
drawing.py Development Notes
============================

For: :mod:`visual.frame.drawing`

.. include:: /common

Future Feature Adds
-------------------

Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Decouple the ReportLab implementation from the SVG vector graphics in :python:`visual.frame.drawing.Drawing`.

        - I don't really want to create domain-specific languages for every type of rendering frame and then layer on a technology adapter.
          That's silly. This suggests make a 'home technology' that everybody else adapts to.  SVG works nicely as choice for home technology
          in the vector graphics `Drawing` frame since it's rendering-engine agnostic in its own right.

Code Review/Adjustments
-----------------------

    - Review: how much measuring do I really need to do for a frame.Drawing when I can scale vector graphics on demand?
      At minimum I need to respect requested sizes and anchor point positioning.
    - Review: look at how a proposed Maybe type would work to get rid of zero-valued defaults in :python:`frame.Drawing`
    -
