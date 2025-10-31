What happens from the Command Line?
===================================

The Python entry point for Kanji Time is in :mod:`kanji_time.py`.

This module provides the CLI interface for executing report generation tasks.
It includes a dynamic report loader, a generic report runner/pagination loop function, and integration points for expanding the report registry.

This is what happens when Kanji Time starts up:

#. Once the user hits "enter" on command line, the function :func:`kanji_time.cli_entry_point` takes over.
#. If the received request is legitimate for a report, Kanji Time passes control to :func:`kanji_time.execute_report`, which will load up the appropriate report driver code and enter a pagination loop.
#. When the report says that it is finished generating pages, Kanji Time exits with a code of 0.

That's it.  That's the happy path in a nutshell.

It's a pretty big nutshell, though.
There's a lot going on behind the scenes.

High Level Components
---------------------

The below diagram outlines the big pieces of the puzzle of generating a Kanji Time report.

.. mermaid::
    :name: comp_CLI_Components
    :caption: Behind the veil: big components supporting the Command Line Interface.

    ---
    config:
        layout: elk
    ---
    graph TB
       CLI["Command-line Interface"]

       DataAggregator["External Data"]

       ReportDispatcher["Report Dispatch"]
       Geometry["Page Geometry"]
       PageLayout["Page Layout Frames"]
       Atomic["Simple (Atomic) Content"]
       Container["Multi-element Frames"]
       Strategies["Page Layout Strategies"]
       Controller["Pagination Loop"]

       RenderingTechnology["ReportLab PDF Generator"]

       KanjiVG["KanjiVG SVG Data"]
       KanjiDict2["KANJIDIC2 XML"]
       JMdict["JMdict-e XML"]
       Radicals["Unicode Radical DB"]

       CLI --> DataAggregator
       CLI --> ReportDispatcher
       CLI --> RenderingTechnology

       DataAggregator --> KanjiVG
       DataAggregator --> KanjiDict2
       DataAggregator --> JMdict
       DataAggregator --> Radicals

       ReportDispatcher --> Geometry
       ReportDispatcher --> PageLayout
       ReportDispatcher --> Controller

       PageLayout --> Atomic
       PageLayout --> Container
       PageLayout --> Strategies


Execution Flow
--------------

Once the CLI resolves the requested report by name and gathers the report's data it enters a page-rendering loop.
The pagination logic interacts with other Kanji Time components as below.
The overriding consideration for this loop is simplicity: the page-rendering loop delegates all the complexity of page layout, tracking data, and deciding page breaks & report completion to the report controller in a Template Algorithm software pattern.

.. mermaid::
    :name: sd_pagination
    :caption: Report pagination loop.

    sequenceDiagram
        participant CLI as CLI (kanji_time.py)
        participant R as Report
        participant D as Report.Data
        participant PDF as DisplaySurface

        CLI->>R: gather_report_data()
        R->>D: build data object
        CLI->>R: instantiate Report
        loop per page
            CLI->>R: begin_page(n)
            R->>PDF: draw()
            PDF->>PDF: showPage()
        end

.. seealso:

    - See :ref:`layout_model` for an overview of the page layout mechanics.
    - See :ref:`builtin_frames` for an overview of the elementary rendering frames.
    - See :ref:`pagination` for more about the mechanics of pagination.
