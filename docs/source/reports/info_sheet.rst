====================
Kanji Summary Report
====================

.. include:: /common

Python module: :mod:`reports.kanji_summary.report`

The Kanji Summary Report is designed to provide rich contextual information for a given kanji character. It complements the practice sheet by giving learners insight into the character's readings, meanings, radical, and dictionary glosses — structured across one or more paginated PDF pages.

Report Structure
----------------

- **Page 1** begins with a full-width banner containing:
  - A large kanji drawing
  - A brief English definition
  - A display of kun/on readings and radical metadata

- **Subsequent pages** feature a compact banner and continue with additional dictionary content formatted as a scrollable, vertically stacked text region.

Nested `RenderingFrame` instances render all content as clients of the control code in :class:`PaginatedReport`.

Implementation Notes
--------------------

This report demonstrates modular layout design:

  - The `gather_report_data` method collects required **Data** as a `KanjiReportData` instance.
  - A :class:`Container` instance hosts **Content Frames** such as `KanjiSummary`, `RadicalSummary`, `FormattedText`, and `HorizontalRule`, that collectively define a report page.
  - A vertical :class:`StackLayoutStrategy` instance manages the **layout** of these content frames within the host container.

----

Automodule Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: kanji_time.reports.kanji_summary.report


The Report Class
----------------

Each KanjiTime report exposes a class named `Report` that implements both the `RenderingFrame` and `PageController` behaviors.

----

Autoclass Documentation
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: kanji_time.reports.kanji_summary.report.Report

The Data Class
--------------

By convention, the top-level data access logic for a report resides inside a python module named :mod:`document.py`.

----

Automodule Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: kanji_time.reports.kanji_summary.document
    :members:

----

Auxiliary Frames
----------------

The Kanji Summary report has historic interest as the underlying prototype for developing Kanji Time as a full application.
It has custom frame logic that illustrates how to do customized layout calculations or manually managing child frames.

Much of the functionality in these frames has been subsumed into the greater architecture.
It now serves as a discussion point in the evolution of the program design.

----

Autoclass Documentation
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: kanji_time.reports.kanji_summary.banner.SummaryBanner

.. autoclass:: kanji_time.reports.kanji_summary.banner.SummaryBannerPage2On

.. autoclass:: kanji_time.reports.kanji_summary.kanji_summary.KanjiSummary

.. autoclass:: kanji_time.reports.kanji_summary.radical_summary.RadicalSummary

----

Alternate entry point
---------------------

A report may also define a function `generate` in its `report` module as an alternate entry point.
The generate function is free to apply any logic it needs for the report independent of the Report class behavior.
This makes it a convenient location for debugging and diagnostics outside of the command line framework.

Autofunction Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: kanji_time.reports.kanji_summary.report.generate

