==============================
Pagination Layout: Page Frames
==============================

Python code file: visual/frame/page.py

The `Page` class represents a single rendered page of a report. It inherits from `Container` and extends the layout model to handle physical page constraints, such as size, orientation, and margins.

Unlike general containers, a `Page` operates within a bounded region defined by its `PageSettings` and manages reusable layout templates through a factory pattern.

Key Responsibilities:

- Establish the printable region using `PageSettings`
- Aggregate child `RenderingFrame` instances and manage their layout
- Orchestrate multi-page output via the controller-driven page loop
- Support flexible pagination schemes (e.g. portrait cover followed by landscape data)

A `Page` is measured and drawn like any other content frame, but must also manage real-world layout constraints such as paper size and margin enforcement.

----

Module Header and API Reference
-------------------------------

:ref:`kanji_time-visual-frame-page-py`
