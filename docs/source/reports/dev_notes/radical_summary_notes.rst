.. radical_summary.py.dev_notes:

====================================
radical_summary.py Development Notes
====================================

For: :mod:`reports.kanji_summary.radical_summary.py`

.. include:: /common

Code Review/Adjustments
-----------------------

    - Factor: convert `RadicalSummary` to be a vanilla horizontally stretchy vertical stack with a minimum size to fit the radical's SVG drawing.
      I don't need to have a customized layout.
