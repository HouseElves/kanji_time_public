Overview
--------

Kanji Time is a living project.
Like all living projects, it has accrued some technical debt out of a preference for releasing a stable well-defined product over chasing perfection.
Beyond resolving technical debt, Kanji Time also offers multiple avenues for adding value through new features rejected for this release.

The following roadmap consolidates immediate engineering tasks and aspirational enhancements.
It is neither a commitment nor an exhaustive wish-list, but a unified vision for keeping Kanji Time flexible, robust, and genuinely useful for learners and as a report generation engine.

Code Adjustments and Enhancements
---------------------------------

**Security:**  

    - Review and harden the security model for report add-ons.
    - Review necessary safeguards against malicious code or bad actors in these add-ons.
    - Consider creating an installer and/or registry that brings a Python report add-on module into Kanji Time with appropriate due diligence towards safety. Review liability ramifications.
    - High priority: tighten the whitelist mechanism with a code hash verification that an add-on hasn't changed.

**Performance:**  

    - Global data loading negatively impacts startup time and perceived responsiveness from the command line.
      Look for opportunities to defer loads to "on demand" that are not simply "moving the pain point".
    - The radical maps and their dependencies are the clear starting point for performance tweaks.
      Investigate deferred loads of them or mitigating their long load time with visual feedback.
    - High priority: progress bars as an intermediate step to gloss over the load time pain.
    - Consider: a local server to provide data across sessions - this work is on the path to making a Kanji Time web service.

**Thread Safety:**  

    - There are many code comments about thread safety which, in retrospect, seem to be over-enthusiastic in the context of the Python GIL.
      On the other hand, Python is inexorably moving towards removing the GIL, so the enthusiasm may be justified.
    - Consider some experimental code that spins up worker threads for each report being generated.
      This will require some forethought about sub-report dependency management.
      The immediate goal would be to stub out dependency concerns to focus on identifying vulnerable global data and instance mutators.
      Focus first on identified code in:

        - radical mapping
        - KanjiSVG loading
        - rendering frame implementations

    - All the report generation code is processor-bound, so *async* isn't appropriate.
      Consider expanding the report workers with a common thread pool for region layouts and other long tasks. 
    - Other considerations for future work include data ownership guarantees, a many-reader/one-writer model, and improved state management for frame classes.

**Linting and Refactoring:**  

    - PyLint flags several "too many" warnings (too many instance attributes, too many locals, etc.).
    - This is pure style: either change the PyLint config to eliminate the warnings or execute on a refactor.
    - Identify portions of the code that are exceptional to the PyLint rules and document them.

Feature and Architecture Roadmap
--------------------------------

**Documentation and Automation:**  

    - Tighten documentation style rules to include diagram annotations and dev notes.
    - Automate extraction and consolidation of code notes, e.g. with standardized `# NOTE` tags. Something off-the-shelf would be nice.
    - Consider integration with lightweight ticketing or PM systems.

**Testing and Hygiene:**  

    - Enforce 100% branch coverage and a clean PyLint run (with documented disables) for every accepted push.
    - Add a documentation page for testing and code hygiene.

**Report Chaining and Meta-Reports:**  

    - Support meta-reports that chain or interleave pages from different reports, creating "themed workbooks" as single PDFs.
    - The backend already supports this in principle with replaceable `Page` instances.
      That support is incomplete - it needs a generalized driver and improved front-end UX.

.. _rendering_technology:

**Rendering Technology Abstraction:**  

    - Pursue rendering-technology-agnostic design.
    - Replace direct ReportLab/Canvas dependencies with abstracted interfaces and adapters building on the current rudimentary abstraction placeholders such as `DisplaySurface`.
    - Decouple vector and text rendering from any single backend.
    - The goal is for a limited set of invariant DSLs (Domain Specific Languages) for "home" technologies.
  
        - The SVG standard is the home technology for vector drawing.
        - Simple HTML-like markup similar to ReportLab's XML is the home technology for text. 
        
    - Standardize coordinate conventions across backends by making details of origin and axis direction specific to a rendering technology invisible under a global setting.
      While this is more the domain of the geometry layer than the rendering engine, the two must work in tandem.

.. _data_plans:

**Data Layer Refactor:**  

    - Load the current XML files into an SQL database - most likely Postgres.
    - Create a DTD parser to generate SQL schema and Mermaid ERDs.
      This is an ideal sub-project to test out Claude Code's abilities.
    - The ultimate goal is to run clustering and NLU algorithms across the XML kanji fact sets.
    - The deeper goal is to connect the PDF pipeline in Kanji Time to the Reports As Code aspect of the ADS project.

.. _layout_and_geometry:

**Layout and Geometry Enhancements:**  

    - Improve the layout coordination and negotiation algorithm in the Container base type.
      The current implementation is expediency, not good design.
    - Add floating containers and z-axis support.
    - Open question: do these add value or just clutter the design?
    - Formalize the size constraint mechanisms, especially w.r.t the idea of a "requested size".
    - Expand the `Distance` type with more powerful constraint models and dependencies.
    - Consider outward unit propagation for aggregate types such as `Extent`, `Pos`, and `Region`.

**State Management and Context:**  

    - Develop a more robust approach to state labels and transitions as a mix-in or context manager.
    - There is danger that classes such as RenderingFrame can fall out of consistency or violate thread safety in the current model.

**Developer Tools and Markup:**  

    - Tighten integration with XML tools with automated code-generation for data classes.
    - Formalize text markup languages for content rendering (potentially RST or a DTD-backed simple HTML) - see :ref:`new rendering abstractions <rendering_technology>`.

**Customization and Configuration:**  

    - Move all user-configurable options to YAML, with in-code help strings and schema support, to streamline configuration and onboarding.

.. _radicals: 

**Radicals and Kana Data Expansion:**  

    - Expand radical and kana data, possibly integrating Wiktionary or similar sources.
    - KanjiSVG already has SVGs to draw kana on practice sheets.
      This work item is to identify, gather, and make available the explanatory material for a supporting "kana summary" report to the "practice sheet" analogous to the "kanji summary" report.

