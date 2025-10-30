.. _highlights_contents:

=================
Design Highlights
=================

Kanji Time favors a hybrid functional-OOP design philosophy that leverages Python's strengths in composition and immutability.
Key parts of this philosophy are a preference for small immutable data objects, severely limited class hierarchy depth, and aggregated behaviors over specialization.

Design Highlights Contents
--------------------------

    - :ref:`philosophy`
    - :ref:`choices`
    - :ref:`weaknesses`

----

.. _philosophy:

Design Philosophy
-----------------

Guiding principles in Kanji Time that govern design choices include the below actions.

#. **Clarity over Cleverness**

   Favor plain well-factored modules, predictable flow, and easily understood composition over clever, obscure, or gimmicky structure.

#. **Practical Purity**

   Hew to clear design ideals wherever possible but also be willing to be pragmatic about breaking purity in a well documented fashion in the
   interest of obtaining results.

#. **Documentation-Driven Development**

   Treat meaningful docstrings, Sphinx integration, and diagrammatic understanding with same level of respect given to the Python code itself.

#. **Extensibility as a First-Class Concern**

   Develop each component to be extensible without requiring invasive changes elsewhere in the codebase.

#. **Add-on Growth is a Desired Outcome**

   Maintain an architecture that is optimized for securely adding new report modules or content frames seamlessly into the Kanji Time ecosystem without harmful impact.

#. **100% Branch Coverage Testing as Design Review**

   Close the code-to-design-review loop by critically examining actual design choices & code assumptions that surface from branch coverage testing.

Back to :ref:`highlights_contents`

----

.. _choices:

Key Design Choices
------------------

**Modular Report Architecture**

  - Clear separation of concerns: data gathering, pagination, rendering.
  - Protocol-based interface via :class:`ReportingFrame` and :class:`PageController` allows pluggable reports.
  - Whitelisting authorized report modules ensures that Kanji Time only executes known code.

**Well-Defined Reusable Layout System**

  - Geometric primitives (:class:`Distance`, :class:`Extent`, :class:`Region`, :class:`Pos`) are expressive and reusable.
  - The content frames and containers separate the positioning of content from the content data itself as distinct concerns.
    This separation allows pluggable layout strategies to position page elements without requiring explicit knowledge of the page data.
  - The Stack-based layout strategy is simple, composable, and well-encapsulated.
  - Differing content types modeled as :class:`RenderingFrame` components are isolated, predictable, and testable.

**Developer Awareness**

  - Development notes document known limitations and opportunities for future enhancement.
  - Mermaid diagrams and documentation are integrated into the codebase as first-class citizens with an eye to rapid on-boarding

**Intentional Design Patterns**

  Kanji Time leverages several well-recognized Design Patterns [GoF]_ in the codebase either explicitly or as emergent behavior.

  *Template Method Pattern*, *Model-View-Controller*

      Used in the CLI dispatch flow for report generation.

  *Composite and Delegation*

      Reports delegate to rendering frames, which may recursively delegate to nested rendering frames.

  *Strategy Pattern*

    Swappable `LayoutStrategy` implementations encapsulate layout behavior.

  *Plugin Architecture*

      Reports are dynamically loaded modules that conform to well-defined entrypoint protocols.

  *Immutable Value Objects*

      Geometry types behave like functional, side-effect-free value objects.

  *Domain-Specific Layering*

      Data (kanji, radicals), presentation (layout/render), and logic (reports) separate cleanly.

  *Class-Level Configuration*

      Many modules configure behavior through attributes rather than external configuration files.

Back to :ref:`highlights_contents`

----

.. _weaknesses:

Design Weaknesses
-----------------

**Responsibility Boundary Ambiguity**

    - There's an unclear distinction of responsibility and ownership between `measure()` and `layout()` in some nested components that makes the :class:`RenderingFrame` protocol inconsistent.

**Overflow Behavior**

    - Kanji Time inconsistently handles or logs discarded content and off-page elements.
    - Kanji Time's "unhappy path" handling of out-of-bounds or overflowing content must be made robust in the next release.

**Thread Safety**

    - Some style and layout elements in Kanji Time are not safe under concurrency.
    - This issue is not critical right now because Kanji Time is single threaded under the Python GIL.
    - PEP 703 and "no-GIL" support in Python 3.14 make robust multi-threading a compelling Kanji Time feature in the future.

**Import Safety**

    - The report add-in mechanism as-implemented has a potential security vulnerability to malicious code that explicit whitelisting mitigates but does not resolve.

**Data Consistency**

    - Kanji Time has minimal sanity checking on imported data.
    - The loaders for the Radical/Unicode/SVG data do not enforce the XML schema or validate against the embedded DTD.

Back to :ref:`highlights_contents`

----

.. [GoF]
    More about the *Template Method*, *Strategy*, *Composite*, and *Delegation* patterns can be found in

        Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides.
        *Design Patterns: Elements of Reusable Object-Oriented Software*.
        Addison-Wesley, 1994.
