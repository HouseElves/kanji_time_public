.. kanji_summary.py.dev_notes:

======================================
Kanji Summary Report Development Notes
======================================

For: :mod:`reports.kanji_summary`

.. include:: /common

Legacy Custom Child Frames
--------------------------

    - The Kanji Summary report has child frames left over from the initial development whose functionality has now been subsumed by generic text and drawing frames with containers.
    - I have kept them as-is as illustrations of how to do customized layout outside of a container + layout strategy.

    .. note::
        These child frames duplicate code.
        They should have their specialized functionality factored out to generic services (if necessary) and then be replaced with standarized containers.

Kanji Summary Modules
---------------------

    .. toctree::
       :maxdepth: 2

       document_notes
       kanji_summary_notes
       radical_summary_notes



