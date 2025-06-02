==============
The Road Ahead
==============

.. include:: /common

Code Adjustments
----------------

    - :ref:`security`
    - :ref:`performance`
    - :ref:`threadsafety`
    - :ref:`linter`

Code Enhancements
-----------------

    - :ref:`customize`
    - :ref:`yaml`
    - :ref:`radicals`

.. _security:

Security
--------
    - I need think about penetration testing and ways to secure the report add-on process for third-party contributions

        - What precautions do I need to take against loading malicious code with LoadModule?

.. _performance:

Performance
-----------

    - the `external_data.radicals.radical_map` and `external_data.radicals.meaning_map` trigger a lot of start-up time activity.
      Rethink this entire mechanism with better awareness of my dependencies and what can be deferred.

        - `external_data.radicals.Radical.__new__` looks like the offender in this process, but this is just the guy that kicks off the start-up issues.
        - Is it worth adding some visual feedback with a progress bar?

.. _threadsafety:

Thread Safety (for a multithreaded future)
------------------------------------------

    - Protect methods (like `kanji_svg.KanjiSVG.load`) with instance mutators with some kind of lock.
    - Maybe provide a guarantee mechanism that certain classs instances only live on one thread at a time?
      Possibly even a many reader / one writer model?
    - the interaction between `external_data.radicals.radical_map`, `external_data.radicals.meaning_map`, and `external_data.radicals.Radical.__new__`
      touches a vast amount of global data.  I need to lock everything down until the load completes.
    - Explicitly setting state in any of the `RenderingFrame` implementations looks sketchy for multiple threads, especially
      :python:`visual.frame.Container` and :python:`visual.frame.SimpleElement`.

        - Have a good look at some of the concepts in :python:`visual.frame.protocol.content.States` for more robust management of state
          transitions via a context manager + associated formal goo.

    - is thread safety an issue in the `kanji_summary.document.KanjiReportData` class?
    - Review :python:`practice_sheet.document.PracticeSheetData` for thread safety issues.

.. _linter:

Linter Complaints
-----------------

    - :python:`external_data.kanji_svg` has several refactoring complaints from PyLint.
      I will be shuffling some code around here later. Bear these in mind.

        - class KanjiSVG - Too many instance attributes (17/7) (too-many-instance-attributes) |rarr| this will go away with an XML refactor
        - class StrokeGroup - Too many instance attributes (12/7) (too-many-instance-attributes) |rarr| ignore, it's a data class
        - method KanjiSVG._load_all_groups - Too many local variables (24/15) (too-many-locals) |rarr| this will go away with an XML refactor
        - method KanjiSVG.draw_strokes - Too many arguments (6/5) (too-many-arguments) (6/5) (too-many-positional-arguments) |rarr| worth investigating
        - method KanjiSVG.draw_practice_axes - Too many local variables (19/15) (too-many-locals) |rarr| worth investigating
        - method KanjiSVG.draw_stroke_steps Too many local variables (16/15) (too-many-locals) |rarr| worth investigating
    - evaluate :python:`StackLayoutStrategy.layout` for factoring - pylint is complaining about too-many-locals
    - :python:`external_data.kanji_svg` has several refactoring complaints from PyLint.


.. _feature_adds:

Future Feature Adds
-------------------

Documentation, Code, Push guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - do I need documentation style rules about what properties go into the Mermaid class diagram:  just @property or all self data?

        - my thoughts are "as appropriate" to the diagram, no hard and fast rules beyond "use your best judgement".

    - convert my template RST to a list of approved dev_notes headings and in the correct order
    - consider # NOTE for automatic dev_note extraction from code and consolidation to the module/class/function header.
    - Anything that I can do to automate dev_note consolidation is a good thing.
      # NOTE[<heading/type>] comes to mind.

        - Examples:  NOTE[Review], NOTE[Factor], NOTE[New Features/Whitespace strategies]

    - Change NOTE to NOTED after extraction?
    - Can I link this up with a ticketing / PM system with Jira or Jira-light or Github or MSFT Tasks?

Testing / Hygeine Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Need doc page for this

      - Require 100% branch coverage tests for a push to be accepted
      - Require a clean PyLint w/ documented "# pylint: disable=" comments

Report chaining
~~~~~~~~~~~~~~~

    - Define meta-reports that can chain or interleave pages (possibly conditionally) different reports into one big reporting job.
    - The prototype use case is the processing multiple kanji in one Kanji Summary report which also interleaves Practice Sheets:
      this output should all land in one big happy PDF as a themed workbook with an theme description page.

        - Oh! That "themed workbook" makes this concept smell like a 'report binder' feature.
        - All the functionality there with different `Page` instances controlling different page layouts, it's just a question of wrapping
          a driver mechanism around it.
        - The back end isn't hard at all, I think passing the same surface through everybody is the key part then delegating to the correct
          report on each page.  Good thing that I have a delegation infrastructure in place :D.
        - The front-end UX? Well, that's deferred just like it is for everything else. We'll hard code instances as needed for now.

.. _rendering_technology:

Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - This feature is shaping up to be a domain-specific language
    - make init_reportlab() part of the technology abstraction & adapter layer by replacing it with a generic technology initialization
    - make a generic display surface provider = :code:`DisplaySurface` is a cheap subclassing stunt to alias ReportLab's canvas
    - make a data formats conversion protocol for technologies, for example

        - this is a customer converter from an Extent to ReportLab's version as a tuple of two floats:

            :python:`page_size = tuple(map(lambda x: x.pt, page_settings.page_size))`

    - going to need some file system handling protocols: ReportLab barfs on pathlib.Path, what other Python conveniences are sketchy?
    - make a generic page-eject - `display_surface.showPage` is ReportLab-specific
    - :python:`visual.protocol.content.DisplaySurface` needs to be a generic protocol for a technology,
      not explicty bound to :python:`ReportLab.canvas.Canvas`
    - Decouple the ReportLab implementation from the SVG vector graphics in :python:`visual.frame.drawing.Drawing`.

        - I don't really want to create domain-specific languages for every type of rendering frame and then layer on a technology adapter.
          That's silly. This suggests make a 'home technology' that everybody else adapts to.  SVG works nicely as choice for home technology
          in the vector graphics `Drawing` frame since it's rendering-engine agnostic in its own right.

    - Decouple the ReportLab implementation from the simple HTML text in :python:`visual.frame.formatted_text.FormattedText`.

        - As in the `Drawing`, I don't really want to create domain-specific languages for every type of rendering frame.
          ReportLab's simple HTML-like XML for text markup seems like a great starting point for a home technology
        - Using the Simple HTML as a home technology suggests as well different adapters for markdown or DocBook.
          I don't want to reinvent PanDoc! So let's keep this simple.

    - With respect to thoughts on handling different coordinate systems in the geometry, a rendering technology will need to supply transforms
      to/from it's native coordinates (and ordinate data type!) and the conventional coordianate system adopted by the geometery.

        - Raises an interesting Q: should the geometry just have a global 'coordinate axis convention' setting that picks up from the
          rendering technology?
        - What if I want to change the convention setting?  Should I have multiple geometries with mapping functions between them?
          I.e. instantiate a geometry with immutable settings and well-known transforms to other geometries.
        - What if I totally change the rules and make one of my geometries projective or inversive... can I make them all cohabit nicely?

    - The text and drawing frames draw heavily on their ReportLab counterparts.
    - Data acquistion needs to be decoupled from its presentation - consider `kanji_summary.document.KanjiReportData` dataclass.
      It has ReportLab technology baked right into it - it should stop at the SVG and Simple HTML layers.
    - One concept for a technology driver is to serve up implementations of RenderingFrame via a factory, sort of how writesvg serves up SVG functionality.
    - Is it worth a generic protocol on behaviours?  I.e  ImplementsReportlab[Drawing] or some such?
    - This feature will also need to settle on some kind of universal coordinate system -- where is the origin and X/Y axis directions.
      It's possible that I can bury this in the `Region` handling, and simply interrogate the technology driver for its preferences.

    - ReportLab handles text overflow - what doesn't fit in the output rectantle gets saved for the next output call.

        - we'll need to handle this situation ourselves in the general flowing output case.
        - this strongly ties into pagination strategies

.. _data_plans:

XML |rarr| SQL Data
~~~~~~~~~~~~~~~~~~~

    - XML |rarr| PostGRES automated conversion

        - eliminate XML in favor of a real database with real SQL queries
        - parse DTDs into a potential schema:

            - already have a solid 100% compliant UTF-8 scanner built on flex
            - need a bison grammar for DTDs |rarr| an easy pick off from XML docs
            - the hard part is the heuristic rules for creating tables and relationships -
              need to put my thinking cap on and flesh this out.

        - the ultimate destination is to run some clustering algorithms and NLU algorithms across my existing Kanji data in an effort pick up
          other exercise sets and out pure curiosity


.. _layout_ideas:

Layouts
~~~~~~~

    - Should there be some kind of synchronization tactic for coordinating flowing output in several frames in the same container?

        - Maybe certain markers that have to align horizontally or vertically across frames?
        - Beware of getting too "meta" on this and making uber-layout strategies controlling layout strategies.

    - Review: Is it worth creating a "text layout" that understands flowable content better than the stacking strategy?

        - Does this even make an interesting split of strategies into "flowing & wrapping" vs "fixed dimensions"?
        - How deep would the split go:  frames? containers? layout strategies?


    - Add support for floating child containers & a z-axis one day to the :python:`visual.frame.Container` one day.

        - Floating frames should manifest as a *strategy* (i.e. a :python:`visual.protocol.layout_strategy.LayoutStrategy` instance) not
          as a Container specialization! _Prefer aggregation over inheritance._
        - But... there may be assumptions in `Container` that will be violated if we introduce a z-axis. Review carefully!

    - I have defined a :python:`RenderingFrame.resize` capability but I'm not using it.

        - It's time to decide if this method should stay or go.
        - A decision either way affects :python:`visual.frame.Container` and :python:`visual.frame.SimpleElement` and the pagination loop.

    - for completeness, I need a "vertical" version of :python:`frame.page_rule.HorizontalRule` - reuse the `StackLayoutStrategy` orientation parameter
    - to be considered a "rule", a `HorizontalRule` frame must span the entire width of the parent container.
      Arguably, a page rule should be considered a part of the layout strategy or a container attribute ("add rule separators" N/S/E/W?).
      In this scenario, thr `HorizontalRule` class becomes a "line" drawing element?  Maybe?

    - a "replicate" container would be really useful:  ContentFrame + # times + a layout strategy

        - the canonical use case is a grid:  replicate this FormattedText frame 20 times and apply a 5x4 grid layout strategy.
        - whether or not there's actually 25 instances or a single "sliding" instance that cycles data in/out for each cell is an
          implementation detail - the important point is that it should *look* to the client that there's 25 distinct instances.

    - headers/footers would also be useful

        - maybe a specialized container for out-of-margin content like headers/footers or even margin notes, revision marks, and line symbols.
        - one header and one footer instance shared by all Page instances in a report (unless there's an override)
        - there's probably enough hooks in the :python:`PageController` protocol to make this work.  If not, add them.

.. _forwarding:

Data Forwarding
~~~~~~~~~~~~~~~

    - This is an architectural feature, not an app feature.
    - Property getter/setter functions don't have to operate on :python:`self` - you could operate on a delegatee target instead.
    - Consider an :python:`@delegated_property(target)` decorator that works like :python:`@property`. A companion `@delegated_setter` too?
    - This would considerably clean up delegatee data handling in the `DelegatingRenderingFrame` mixin and make :python:`Protocol`
      delegation smarter.

    - On a different use case, it would be convenient to seemlessly (i.e. without developer action) propogate unit properties
      on the `Distance` type (or any other type) outwards to types that aggregate `Distance` instances (such as `Extent`, `Pos`, `Region`)

      - I'm thinking that somthing like :python:`extent.in` yields a namedtuple (or anonymous :python:`tuple`?) of floats with :python:`.width` and :python:`.height` in inches.
        The property :python:`in` propogates upwards from the `Distance` instances in the `Extent` instance.
      - This may require a completely different mechanism from the :python:`@delegated` decorators.
      - Since I'm such a big fan of decorators, maybe :python:`@units(dimension)` -- see the `Distance` dev notes.

    - What about layout math? See notes on `Container.measure`.

        - Consider:  is "percent of X" where X is property live-delegated to some other `Distance` instance?
        - Of course, data forwarding and delegates in this use case also raises the spectre of change notification & when are they necessary.

Styles
~~~~~~

    - The styles that come in from ReportLab are very much JavaScript-inspired - they don't really play well in the Python idiom
    - Let's create something similar but derived off a ChainMap
    - Of course, we can also use a ChainMap for the style names
    - Consider a class/function decorator @styled:

        - provides a local `style` symbol implicity if it's not passed as an argument.  Put the default style name in the decorator.
        - intercepts kwargs off the function call to chain style overrides onto `style`
        - the page factory fetcher should also hand styling and overrides
        - pass the style plus any explicit overrides down to any called @styled function
        - useful in the Kanji Summary and Practice Sheet reports

    - Use case in the kanji vector drawings to change up the pen color for the radical
    - Give a YAML interface to configure all this.  Or a 3rd party CSS parser too, maybe?
    - See:

        - `reports.kanji_summary.KanjiReportData` methods
        - `reports.kanji_summary.document.build_data_object`
        - `external_data.kanji_svg.KanjiSVG`

      for some places where there are hardcoded dictionary styles.
    - The important part is a push/pop into stylable methods to set a sytle context
    - Use the new style application mechanism for drawing debug frame rectangles.


Pagination Enhancements
~~~~~~~~~~~~~~~~~~~~~~~

    - Instantiate a `PaginatedReport` with keyword arguments for the various layouts attached to a dict of `RenderingFrame` instances
      for content?
    - `PageController.begin_page` returning `None` is a bit clumsy for "no page" when coupled to the overlap with the state flags.

.. _whitespace_strategies:

Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - Consider adding a `redistribute_whitespace` method to the `RenderingFrame` protocol.

        - This implies an idea of `fixed` vs `variable` portions of layout within a frame.
        - Certain minimum whitespace padding would get incorporated into the `fixed` size.
        - Can I accomplish this just by redoing `do_layout` or are there some assumptions that I bake into `redistribute_whitespace` to make
          it less weighty?  One of these would clearly be about `fixed` sizes.

    - The anchor point semantic isn't really well defined in `Container` vs `RenderingFrame` instances.  See :python:`Container.do_layout`.
    - The :python:`frame.SimpleElement` class has a note about maybe passing an anchorpoint to :python:`RenderingFrame.do_layout` to position
      the layout in the extent?

        - I am suspicious of adding an anchor-point parameter to :python:`RenderingFrame.do_layout` because it adds more nuance to the `extent`
          parameter -- which is already semantically ambiguous.
        - Consider how `Distance` constraints can lift the semantic ambiguity by baking intention into the `extent` parameter.

    - The "evenly distributed" algorithm for whitespace allocation in :python:`Container.measure` is the canonical use case for having
      whitespace allocator strategy types.
    - :python:`Container.do_layout` has a note that "We don't care about inter-element gaps - the frame is responsible for its own explicit margins."
      How does this fit into any changes or consistency-normalization in whitespace handling?
    - :python:`FormattedText.getSpace{After|Before}` should be part of a `PaddingService` mix-in?

        - not part of a whitespace strategy b/c these are static constraints to a frame
        - concept for a `PaddingService` is a standard set of properties that supply constraints to a strategy

    - does a layout strategy own a whitespace strategy or does this come in on the measure/layout calls as a parameter?

        - Regardless, I'm going to need some kind of default whitespace handling in all of the `LayoutStrategy` instances if a whitespace
          strategy is not provided for :python:`LayoutStrategy.measure` or :python:`LayoutStrategy.layout`.
        - Maybe create a default strategy that gets initialized with some minimum inter-frame padding does the even-distibution thing like
          I'm doing now:  this would be an easy first step to have a look at what this Whitespace strategy architecture would imply.

    - Need to make slop whitespace handling configurable through some kind of passed function like the layout strategies.
    - Could also add a property "accepts whitespace" to a RenderingFrame - parameterize it by AnchorPoint flags.
      The property indicates which side of a rendering frame against which it accepts arbitrary whitespace additions.

        - NB: this idea may not play well with horizontal vs vertical stacking strategies because of its absolute (vs relative) nature.
        - Consider a contextual or semantic variant similar to how "stack_dim" / "other_dim" work in `StackLayoutStrategy`

    - There's a lot of notes about removing whitespace consideration from measure.

        - I'm no longer convinced that this is a correct tactic.
        - The two frame styles of flowing and fixed boundaries handle whitespace somewhat differently
        - There should be a tight coupling to the intended _simple_ `Distance` constraint mechanism and whitespace allocation.

    - measure() should certainly be returning an _minimum_ size necessary but it could include the host frame's own internal
      whitespace management.
    - whatever the outcome on this issue, it strongly affects the semantics of the size properties of `RenderingFrame` such as
      `requested_size` et al.

    - The anchor point semantic isn't really well defined.

        - Am I positioning inside the host container or inside the frame?
        - The code seems to take both points of view in different places - drawings vs flowing text.

    - The hardcoded spacing between `Practice Sheet` elements is another code case for rethinking the whitespace handling.

.. _sizing:

Size Contrants
~~~~~~~~~~~~~~

    - The "requested_size" property of the `RenderingFrame` is a little wishy-washy - I've established that it's a desired size to reserve
      but it's being used inconsistently
    - Formalize a constraint model on the `Distance` type: "exactly 2in" or "at most 50% of parent" or "at least 120pt", etc.


.. _new_distance:

Enhanced `Distance` features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - The :python:`layout.Distance` constaint model is primitive
    - I'm not entirely happy with "stretchyness" tied to a unit.
      I'm thrilled with it conceptually, but I'm not sure about how I feel about how I've implemented it.
    - RST likes "pc" for percent.
    - `RenderingFrame.measure`, `RenderingFrame.do_layout` and `RenderingFrame.draw` are always the intended `Distance` clients.
      These methods drive constraint and other new `Distance` features.  Review the code in existing implementations.
    - the minimum constraint case is going to be at_least, at_most, and between.  However I go, I need to ensure consistent semantics.

        - maybe move away from fixed flags and define a distinct `Constraint` type?
        - this gets to an "apply constraints" semantic that adjusts a distance or a "satisfies constraints" that checks.
        - raises the possibility of constraint expressions linked with logical connectives.
        - who owns a constraint?  Maybe it should be decoupled from the `Distance` type.
        - how do constraints interact with equivalence? Consider a case for "at least 5" equal to anything bigger or equal to 5.
          This case sounds more like a "matches" semantic, not an "equivalence" semantic.

    - `Distance` dependencies couild be useful too.

        - This is already a necessity to implement percentages on proportional layouts
        - Dependencies also naturally arise with my new property delegation model
        - Does this generalize to more expressions?  I.e width = 1.62*height -- but I manage the height value during layout and
          propogate it through its dependers by invalidating completed layouts?  `measure` would have to create a top-sorted recalc chain
          as a side effect to pass through/available to `do_layout`.
        - Eeek! a gradient descent optimization during layout... the mind boggles... let Torch deal with the details - too fancy but an
          interesting thought.

    - Outward propagation of the "unit" properties to types that contain them?  From the Data Forwarding notes on "kanji_summary.py":

        - It would be convenient (at least for debugging) to seemlessly propogate unit properties on the `Distance` type (or any other type)
          outwards to types that aggregate `Distance` instances (such as `Extent`, `Pos`, `Region`)
        - Something like :python:`extent.in` yields a tuple of floats with :python:`extent.width` and :python:`extent.height` in inches.
          The property :python:`in` propogates upwards from the `Distance` instances in the `Extent` instance.
        - This will require the help of the new property delegation and data forwarding featrues.

    - Much longer term vision:

        - a Measurement protocol with L/T/M dimensions [or even $ and counting categries], fuzzy/crisp aspects and arithmetic.
        - the Measurement owns its own units, conversion tables, and parser just like Distance does
        - create Measurements on-the-fly for products and quotients like "Newton-metres" or "metres/second".
        - maybe even expose some common constants on specific well-known measures.

Generic Measures &  Geometry Enhancements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor all the arithmetic out to general purpose classes.
      There's experimental code mapping op groups into abstract algebra objects - monoid, group, field et al.
    - `__floordiv__` and `__truediv__` can operate on other measures of the same *unit* to produce a pure number.
    - Should there be a pure number (or pure ratio) unit in all the measure types?
    - Think about axis position and direction conventions - there's a clean way to do this with FP by passing around
      binary combinators appropriate to a coordinate system that map down to the conventionally oriented binops.
      The choice of conventional orientation doesn't matter as long as it's convenient and universal.

        - Look at :python:`StackLayoutStrategy.layout` -- there's some explicit coordinate assumptions.
          Probably the same story in :python:`Container.do_layout`

    - do I need an absolute and relative position in the geometry?
      Better named as `Offset` vs `Pos`.  :python:`Offset == (dx, dy)`.

        - This could impose a much pickier set of type constraints that ripples throughout the code.

            - `Pos` - `Pos` |rarr| `Offset`
            - `Pos` + `Pos` |rarr| meaningless.
            - `Pos` + `Offset` |rarr| `Pos`

          Whether this is a good or bad thing reamains to be seen. I *_do not want to overgeneralize_*.
        - Does this also mean two kinds of regions:  relative vs absolute |rarr| a `Subregion` maybe?
          :python:`Subregion == (Offset, Extent)`

    - a full featured notion of absolute and relative may need an awareness of global coordinates throughout
      *which violates one of the fundamental design commandments* that frames can be positioned arbitrarily just by moving their
      origin point.

        - There is merit to an absolute region in that the physical page itself has specific regions that *cannot* move: header, footer,
          t/b/l/r margins, printable area.
        - A root absolute region provides a single source of truth about the material origin of the entire coordinate system and about
          boundaries for relative regions that live inside of it.
        - I still worry that it will unnecessarily complicate code or tie my hands in the future trying to live up to an abstraction purity.


State labels/transition Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - I actively dislike having explict state labels out of an enum.
      They have a nasty habit if getting out of synch with the actual set of data values that they describe.
    - Consider the notes on `visual.protocol.content.States` about how to keep synchnonization.
    - Define a mix-in for explicity state transition behavior with:

        - `in_state` method that maps instance data to a state-enum value rather than just reading a cached state-enum.
        - `check_state` method that confirms the instance data conforms to a state-enum value or set of values.   __contains__ would be awesome for the **in** keyword.
        - `ready_for` method that checks if the instance can make a transition from its current state to some new one.

    - have a context manager "with doing_transition_to(States.some_state):" that has smarts to

        - verify that the object is a state that _can_ move to the target state
        - manage rollback should the transition fail and/or raise appropriate errors
        - handle thread safety issues

XML Utilities
~~~~~~~~~~~~~

    - Pull in the XML-specific operations in the Kanji SVG loader
    - Connect dataclasses such as kanji_svg.KanjiSVG.StrokeGroup with the DTD parser such that I can autogenerate them from an XML source
    - Associate XML tag QNames with their property dataclass as an attribute.
      Consider an @XML_tag decorator on top of @dataclass to fill this in by magic.
    - Maybe tag dataclasses can include a `handler` classmethod that can go into a tag|rarr|handler dispatcher.
      If I'm going there, generic dispatching code would be convenient building on what's in `functools`.
    - Think about data cleansing for parameters on a tag dataclass:  who owns this code?
    - Add some indent management to the :python:`utilities.xml.xml_tag` context manager - possibly by layering it around `StringIO`.


Formalize Simple HTML text markup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Just like it says on the tin:  I need to specify Simple HTML formally for compliance testing.
    - Extract from ReportLab, tweak, and create a DTD for it.

        - Why go with XML when I hate XML? The DTD |rarr| RDBMS schema project.
          I'd love to be able to suck text into a database on my terms and XML approach enhances the yield of my IP.
        - I'd end up with semantic label tags on structural document elements.

    - Maybe RST would make for a better home technology for formatted text?  Explore the trade-offs.

.. _customize:

Customization
~~~~~~~~~~~~~

    - Make the reporting package path a configurable option. We're half way there with the alias |rarr| module map in VALID_REPORTS

.. _yaml:

YAML Settings
~~~~~~~~~~~~~

    - Move all user-configurable options to a YAML (or YAML-like) document
    - Need to include help strings, preferably baked right into a setting schema-like object

.. _radicals:

Extended Radical/Kana Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Flesh out radical information with new sources giving some better etymology and history
    - Hiragana + Katagana: KanjiSVG has drawings for these characters but I have no backing data store to tell a story about them

        - Wiktionary seems to have a lot of information about the other kana - I've experimented with some REST queries to extract it
        - Presenting these data may need a variant on the KanjiReport unless I can shoehorn the input into the right spots on a
          `KanjiReportData` instance.




