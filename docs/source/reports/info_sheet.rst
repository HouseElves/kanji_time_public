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

All content is rendered using nested `RenderingFrame` instances coordinated through the standard `PaginatedReport` controller.

Implementation Notes
--------------------

This report demonstrates modular layout design:

  - **Data** is collected by `gather_report_data()`, returning a `KanjiReportData` instance.
  - **Content Frames** include `KanjiSummary`, `RadicalSummary`, `FormattedText`, and `HorizontalRule`, composed inside a `Container`.
  - **Layout** is managed with a vertical `StackLayoutStrategy`.

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

By convention, a report implementation puts all of its top-level data access logic inside a python module named :mod:`document.py`.

----

Automodule Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: kanji_time.reports.kanji_summary.document
    :members:

----

Auxiliary Frames
----------------

The Kanji Summary report was the underlying prototype for developing Kanji Time as a full application.
It has custom frame logic that illustrates how to do customized layout calcuations or manually managing child frames.
Much of the functionality in these frames has been subsumed into the greater architecture - but I have left these 'as is'
as a discussion point in the evolution of the program design.

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

A report may also define a function `generate` its `report` module as an alternate entry point.
The generate function is free to apply any logic it needs for the report independant of the Report class behavior.
This makes it a convenient location for debugging and diagnostics outside of the command line framework.

Autofunction Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: kanji_time.reports.kanji_summary.report.generate

