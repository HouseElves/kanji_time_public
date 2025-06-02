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

All content is arranged vertically using the `StackLayoutStrategy`, and drawn using `ReportLabDrawing` and `FormattedText` components. No banners or glossary content are included — this report focuses purely on handwriting practice.

Implementation Notes
--------------------

- `gather_report_data()` returns a `PracticeSheetData` object with lazily evaluated drawing content
- Stroke diagrams and practice areas are SVGs converted on demand to ReportLab graphics
- The report itself inherits from both `PaginatedReport` and `DelegatingRenderingFrame`
- Only a single layout is used: `"practice_sheet"`

----

Automodule Documentation
------------------------

.. automodule:: kanji_time.reports.practice_sheet.report
    :members:

The Data Class
--------------

By convention, a report implementation puts all of its top-level data access logic inside a python module named 'document.py'.

----

Automodule Documentation
------------------------

.. automodule:: kanji_time.reports.practice_sheet.document
    :members:

