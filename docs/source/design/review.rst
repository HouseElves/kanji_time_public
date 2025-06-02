.. _highlights_contents:

=================
Design Highlights
=================

The code architect, developer, and doc author for Kanji Time, Andrew Milton, has a strong preference for the clean hybrid Functional-OOP driven designs that Python is particularly well suited for.
A crucial part of the Kanji Time design philosophy is preference for small immutable data objects, severely limited class hierarchy depth, and aggregated behaviors over specialization.

Design Highlights Contents
--------------------------

    - :ref:`philosophy`
    - :ref:`choices`
    - :ref:`weaknesses`

----

.. _philosophy:

Design Philosophy
-----------------

Guiding principals in Kanji Time that govern design choices include the below actions.

#. **Clarity over Cleverness**

   Favor plain well-factored modules, predictable flow, and easily understood composition over clever, obscure, or gimicky structure.

#. **Practical Purity**

   Hew to clear design ideals whereever possible but also be willing to be pragmatic about breaking purity in a well documented fashion in the
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
  - Whitelist mechanism ensures only authorized report modules are executed.

**Well-Defined Reusable Layout System**

  - Geometric primitives (:class:`Distance`, :class:`Extent`, :class:`Region`, :class:`Pos`) are expressive and reusable.
  - Positioning content and managing content data are seperated concerns via content frames, content containers and pluggable layout stratagies.
  - The Stack-based layout strategy is simple, composable, and well-encapsulated.
  - Differing content types modeled as :class:`RenderingFrame` components are isolated, predictable, and testable.

**Developer Awareness**

  - Ideas for future growth and review notes about code weak points in well-labeled review and development notes reflect active thinking and design foresight.
  - Mermaid diagrams and documentation are integrated into the codebase as first-class citzens with an eye to rapid on-boarding

**Intentional Design Patterns**

  Kanji Time leverages several well-recognized Design Patterns [GoF]_ in the codebase either explictly or as emergent behavior.

  *Template Method Pattern*, *Model-View-Controller*

      Used in the CLI dispatch flow for report generation.

  *Composite and Delegation*

      Reports delegate to rendering frames, which may recursively delegate to nested rendering frames.

  *Strategy Pattern*

      Layout behavior is encapsulated in swappable `LayoutStrategy` implementations.

  *Plugin Architecture*

      Reports are dynamically loaded modules that conform to well-defined entrypoint protocols.

  *Immutable Value Objects*

      Geometry types behave like functional, side-effect-free value objects.

  *Domain-Specific Layering*

      Data (kanji, radicals), presentation (layout/render), and logic (reports) are separated cleanly.

  *Class-Level Configuration*

      Many modules configure behavior through attributes rather than external configuration files.

Back to :ref:`highlights_contents`

----

.. _weaknesses:

Design Weaknesses
-----------------

**Responsibility Boundary Ambiguity**

    There's an unclear distinction of responsibility and ownership between `measure()` and `layout()` in some nested components
    This makes the :class:`RenderingFrame` protocol a little wishy-washy in places.

**Overflow Behavior**

    Discarded content and off-page elements are inconsistently handled or logged.
    Robustness on the "unhappy path" handling of out-of-bounds or overflowing content is a significant concern for the next round of development.

**Thread Safety**

    Some style and layout elements are not safe under concurrency.
    This isn't that much of a concern since Kanji Time is single threaded under the Python GIL right now.
    However, changes coming to the GIL could make robust multi-threading a more compelling story to have in Kanji Time.

**Import Safety**

    There is potential security vulnerablilty in the report add-in mechanism as-implemented that is mitigated by explicit whitelisting of report modules.

**Data Consistency**

    There is minimal sanity checking on imported data - it simply wasn't a priorty for this round of developement.
    Radical/Unicode/SVG alignment is fragile and lacks schema enforcement.

Back to :ref:`highlights_contents`

----

.. [GoF]
    More about the *Template Method*, *Strategy*, *Composite*, and *Delegation* patterns can be found in

        Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides.
        *Design Patterns: Elements of Reusable Object-Oriented Software*.
        Addison-Wesley, 1994.
