=====================
Practice Sheet Report
=====================

Python module: `reports.practice_sheet.report`

The Kanji Practice Sheet generates stroke order diagrams and blank practice grids to help learners build muscle memory for drawing kanji or kana. It presents these elements in a visually balanced vertical layout suitable for printing or digital annotation.

Report Structure
----------------

The layout includes:
- A **stroke diagram** showing each stroke step-by-step, laid out across one or more rows depending on character complexity
- A **practice heading** and **grids** laid out in multiple strips
- Optional headings for clarity

All content is arranged vertically using the `StackLayoutStrategy`, and drawn using `ReportLabDrawing` and `FormattedText` components. No banners or glossary content are included - this report focuses purely on handwriting practice.

Implementation Notes
--------------------

- `gather_report_data()` returns a `PracticeSheetData` object with lazily evaluated drawing content.
- The report control logic converts SVG graphic commands to ReportLab graphics on-demand to render stroke diagrams and practice areas.
- The report itself inherits from both `PaginatedReport` and `DelegatingRenderingFrame`
- It uses only a single layout: `"practice_sheet"`


The Data Class
--------------

By convention, the top-level data access logic for a report resides inside a python module named :mod:`document.py`.

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-reports-practice_sheet-report-py`
:ref:`kanji_time-reports-practice_sheet-document-py`
