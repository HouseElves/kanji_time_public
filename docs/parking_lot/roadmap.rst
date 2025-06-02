=======
Roadmap
=======

This roadmap captures the current state and forward-looking plans for the Kanji Time project.

Immediate Post-Freeze Actions
-----------------------------

- Finalize documentation pass:
  - Polish ``figures.rst`` cross-references and verify ``:name:`` / ``:ref:`` anchors.
  - Move developer notes into clearly marked **Developer Notes** sections or appendix pages.
  - Standardize docstring formatting, especially around embedded Mermaid diagrams.
  - Add a quickstart or top-level README in Sphinx if missing.

- Close out low-hanging TODOs:
  - Add missing citations (e.g., GoF Template Method).
  - Clarify placeholder or speculative docstrings.
  - Annotate thread safety concerns (e.g., with ``@not_thread_safe`` markers).

Documentation + Review Roadmap (Stable State)
---------------------------------------------

- Diagram Enhancements:
  - Coordinate system walkthrough for ``Region``, ``Pos``, and anchor positioning.
  - Slop distribution logic for ``StackLayoutStrategy``.
  - Optional: fallback overflow rendering visualization.

- Developer-Facing Tools:
  - Add layout diagnostic overlay or debug mode with bounding boxes.
  - Write Sphinx page for report plugin guide (protocol checklists).
  - Add CLI flag to dump unresolved kanji or layout anomalies.

Post-Freeze Design Review
--------------------------

- Pagination Lifecycle:
  - Clarify ``measure()`` and ``layout()`` delegation boundaries in ``reports/controller.py``.
  - Consider UX options for unclaimed layout elements (warn, paginate, overflow).

- External Data Consistency:
  - Validate radical and SVG mappings.
  - Add data coverage scripts for unmatched strokes or glyphs.
  - Normalize internal schema for Unicode, radicals, and SVG layers.

Optional Future Work
--------------------

- Multi-report chaining into one PDF output session.
- Module sandboxing or registration-based report validation.
- Unified schema for KanjiVG/Unicode/radical data ingestion.
- Automated report generation coverage testing.
