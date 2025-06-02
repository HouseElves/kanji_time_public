Overview
--------

Kanji Time is a living project. Like all living projects, it has accrued some technical debt.

Several areas should be improved or refactored for robustness and completeness. In some cases, I deliberately deferred these improvements to avoid destabilizing a working release or to avoid scope creep. There are also multiple avenues open for adding new value.

The following roadmap covers my current priorities, open design questions, and directions for future work. Some are immediate engineering tasks, others are aspirational enhancements that could push Kanji Time into new territory.

Code Adjustments and Enhancements
---------------------------------

**Security:**  
I need to review and harden the security model for report add-ons. There is no way I could ever create an installer or registry for third-party add-ons without basic safeguards against running malicious code. As an intermediate step, I should tighten the whitelist mechanism by possibly including some form of code fingerprinting.

**Performance:**  
Startup time is affected by global data loading; especially in the radical maps and their dependencies. This is a strong candidate for lazy loading, deferral, or (at minimum) visual feedback with a progress bar for long initializations.

**Thread Safety:**  
If Kanji Time eventually goes multi-threaded, I need to guard global data and instance mutators.
I've highlighted code for attention in the radical mapping, KanjiSVG loading, and in some rendering frame implementations.
Future work includes locking or ownership guarantees, a many-reader/one-writer model, and improved state management for frame classes.

**Linting and Refactoring:**  
PyLint flags several “too many” warnings (instance attributes, locals, etc.) in KanjiSVG and layout code. Some of these will resolve as the codebase is refactored; others (such as large data containers) will remain and be documented.

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

    - Support meta-reports that chain or interleave pages from different reports, creating “themed workbooks” as single PDFs.
    - The backend already supports this in principle with replacable `Page` instances, but a generalized driver and improved front-end UX are needed.

.. _rendering_technology:

**Rendering Technology Abstraction:**  

    - Pursue rendering-technology-agnostic design.
    - Replace direct ReportLab/Canvas dependencies with abstracted interfaces and adapters building on the current rudimentary abstraction placeholders such as `DisplaySurface`.
    - Decouple vector and text rendering from any single backend.
    - This is going work towards some invariate DSLs for "home" technologies, although I'd prefer to limit that kind of work:
  
        - The SVG standard should be the home technology for vector drawing.
        - A very simple HTML-like markup similar to ReportLab's XML should work for text. 
        
    - I also intend to standardize coordinate conventions across backends - this is going to be and interesting side problem related to ironing out wrinkles in the geometry layer.

.. _data_plans:

**Data Layer Refactor:**  

    - Load the current XML files into an SQL database - most likely Postgres.
    - I have started on a DTD parsing with schema inference to do this automatically.  I have already built a solid spec-complient UTF-8 parser as a starting point (portfolio link to this pending).
    - Ultimately, I'd like the ability to run clustering and NLU algorithms across the XML kanji fact sets.
    - Far, far down the road: I'd like to link my reports-as-code project (portfolio link also pending) into the data layer once it's in better shape and once I get Kanji Time more feature-rich for non-technical end-users.

.. _layout_and_geometry:

**Layout and Geometry Enhancements:**  

    - Improve the layout coordination and negotiation algorithm in the Container base type.  What I've got works, but I don't get a warm fuzzy from it.
    - Add floating containers and z-axis support.
    - Add some whitespace allocation strategies to work in tandem with the layout strategies.  This may be a blind-alley.
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
    - KanjiSVG supports kana drawing already, but a backing data store is needed for explanatory material.

----

This roadmap is intentionally ambitious. Not every point will land in the next release, but each helps ensure Kanji Time remains flexible, robust, and genuinely useful: for my studies, for other learners, and as a growing report coordination engine.