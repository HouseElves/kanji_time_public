Report Output
=============

The `reports` module provides a pluggable, extensible, and layout-aware architecture for generating Kanji Time output sheets in PDF format using ReportLab. It currently supports two major report types:

    - `Kanji Summary Report` — displays readings, radicals, and dictionary definitions for a glyph
    - `Practice Sheet Report` — presents stroke order diagrams and blank practice grids

Each report implements the `RenderingFrame` and `PageController` protocols, coordinating layout and pagination using reusable content frames and layout strategies.

Individual report modules provide:

    - a `Report` class conforming to the rendering and controller protocols,
    - a `gather_report_data()` method to prepare glyph-specific input, and,
    - a `generate()` method for batch execution, debugging, or CLI use.

Reports define **named page layouts** using symbolic layout names (e.g., `"first page"`, `"practice_sheet"`) to support multiple page templates. Layouts are rendered by delegating to nested content frames via the `DelegatingRenderingFrame` base class. Controllers manage flow using the `PaginatedReport` mixin.

This architecture cleanly separates concerns:

    - `PaginatedReport` handles page lifecycle and switching
    - `DelegatingRenderingFrame` forwards rendering to active pages
    - `ReportData` objects (e.g. `KanjiReportData`, `PracticeSheetData`) encapsulate all content


Framework Classes
------------------

The key to the process is using the PageController protocol and its derived PaginatedReport mixin to take care of all the bookkeeping.

.. automodule:: kanji_time.reports.controller
    :members:


Putting it together: from raw data to output
--------------------------------------------

All Kanji Time reports share the same architecture as shown in the sequence diagram below.

.. mermaid::

    sequenceDiagram
        participant Data as External Data
        participant Report as Report Instance
        participant Page as Page Container
        participant Frame as Content Frame(s)

        Data->>Report: gather_report_data()
        activate Report
        Report->>Page: create_page()
        Page-->>Report: Page instance
        Report->>Page: add(Frame children)
        loop for each page
            Report->>Page: begin_page(n)
            Page->>Frame: begin_page(n)
            Page->>Frame: measure()
            Page->>Frame: do_layout()
            Page->>Frame: draw()
        end


---

Package symbols in 'reports'
----------------------------

.. toctree::
    :maxdepth: 2

    info_sheet
    practice_sheet


