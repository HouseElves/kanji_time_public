.. include:: /common

Code Review/Adjustments
-----------------------

kanji_time.py
~~~~~~~~~~~~~

    - Review: add the page's settings to a `PageController` property?
    - Review: there's overlapping functionality with `begin_page() == True` and `States.have_more_data`
    - Add short/long help string properties to the report implementation's `Report` class for use in the CLI --help=<report_alias>.
    - Make a more robust command dispatch model that consumes an argparse.Namespace and produces a Command instance of some kind.
    - Make failure cases funnel into a common error exit function that imposes consistent failure reporting strings and formats.
    - Define and document a set of exit codes for bash scripting: current codes are already in the Sphinx .RST tree
    - Factor: package all the ReportClass validation into one happy little function in :python:`kanji_time.execute_report`...
      perhaps even make a "ReportPlugIn" protocol, even?

settings.py
~~~~~~~~~~~

    - Review: avoid using strings directly on file system locations.
      This may not be 100% possible because of 3rd party technology limitations.
      I.e. ReportLab does not play well with pathlib.Path instances.

visual/protocol/content.py
~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: other properties on `RenderingFrame` such as "clipable"?
    - Review: why am I not using :python:`utilities.general.coalesce_None` and its ilk to fill in missing values?
      Doesn't Extent have a `coalesce` classmethod?
    - Review: the `RenderingFrame` protocol is pretty bossy about how much data that it wants.
    - Review: several notes removed from :python:`RenderingFrame.measure` method are addressed below

        **Q**: should I  be returning a width/height range and a function relating max_width |rarr| min_height and max_height |rarr| min_width?

        **A**: this idea was addressing flowables where height is a function of width - it's been subsumed with better layout logic.

        **Q**: why do I even have to pass and return an Extent?

        **A**: the passed extent is the maximum space for the frame on a page. We return a minumum space required within that passed Extent.

        **Q**: how about a "requires remeasure" for dimension changes?

        **A**: this will be addressed in a `Distance` dependency model external to the frame.

external_data/kanji_svg.py
~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: does it make sense to mix caching with singletons?
    - Explore: is making a `cached_dict` type exploiting @lru_cache a reasonable abstraction?
    - Factor: pull out the Kanji SVG XML loader from the draw
    - Review: does DFLT_GLYPH_SIZE still belong to the KanjiSVG class? Make it a global constant?
    - Review: add strict type aliases for special purpose strings: SVG commands, Kanji parts, etc.?

        - consider a more active type that includes a "data cleanser" to normalize known input variants for XML parameters
        - Review: look at the svg_transform.Transform class in this context- maybe include specialized parsers?

    - Explore: is it worth creating Maybe-type wrappers? Python's None semantics are somewhat old-fashioned.
    - Review: `kanji_svg.KanjiSVG._load_all_groups` mutates `self` data attributes (such as _groups) directly instead of properly
      returning the data.
    - Factor: create a dispatch dictionary associating tags to tag handlers
    - Review: do the `completed_{attribs, groups}` audit sets in `kanji_svg.KanjiSVG._load_all_groups` need to be distinct?
    - Factor: eliminate the need for the `image_size` parameter in `kanji_svg.KanjiSVG.draw{glyph, stroke_steps}`.

        - Review: I could probably do this by instiating a drawing factory with a default image size.  Does that make sense in the
          abstractions?
        - Review: The whole drawing factory concept seems off.  I should be able to late-bind an image size whenever I want.
          The drawing instance itself is only a recipie for generating text, not the text itself.

    - Factor: replace the `loaded` flag on `kanji_svg.KanjiSVG` instances with a computed property
    - Review: consider a more efficient candy-stripe loop in `kanji_svg.KanjiSVG.draw_practice_axes` when drawing diagonal lines.
    - Review: express the image pixel size calculation as an inner product in `kanji_svg.KanjiSVG.draw_cell_dividers`?
      I would only go here if I have a more drawing flexible framework around this logic.
    - Review: should the `kanji_svg.KanjiSVG` class have more spacing options baked into the instance: inter-step margins, top/bottom margins?


external_data/settings.py
~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: can I do better for the `external_data.settings.PROJECT_ROOT` string and use a stdpath.Path?
      `PROJECT_ROOT` is specifically for Sphinx so it's a little less whiney.

        - is `PROJECT_ROOT` even in the correct settings module?


visual/frame/container.py
~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor: PRIORITY - remove the `update` method from the :python:`visual.frame.container` - this is an ugly hack and the use case for it is
      no longer relevant.
    - Review: how does an AnchorPoint interact with a Container.
    - Review: consider "Partially Reusable" as a container sub-state of reusable?  is this worth the effort? or meaningful?
    - Factor: how do child frames and the Container handle a begin_page request? This is a little wishy-washy.

        - Who handles passing the `begin_page` message along?
        - Is recursing through the child frame tree a good idea?
        - Commit one way or another in :python:`Container.begin_page`

    - Review: is the two-pass child measurement algorithm in :python:`Container.measure` really the right way to go?
    - Review: take a critical look at the share-evenly strategy for whitespace in :python:`Container.measure`.
    - Review: the "deferred measure" case for stretchy dimensions in :python:`Container.measure` isn't very robust.
      It works now, but this is a bug farm waiting to happen not just with unhandled failure modes but also with sub-awesome algorithm design.

        - There's no hard limits on space allocation
        - There's no overflow checking
        - There's no "negotiation" with children to squeeze frames together
        - :python:`Container.measure` is the canonical use case for baking a more robust constriant mechanism into the `Distance` type.
          See the development notes for `Distance` for more details.
        - Things go wonky when any part of an extent goes negative or even falls below a minimum content threshold
        - Would handling page-overflows via an exception make sense? Is it Python idiomatic?

    - Factor: allowing Extent instances to be polymorphic through non-geometry types seems sketchy.
      See the intractions between :python:`Container.measure` and :python:`Container.do_layout` and :python:`LayoutStrategy.measure`.
      I am sub-enthused.
    - Review: do I need to anchor a child in the parent, which affects my computed origin, or myself?

visual/frame/drawing.py
~~~~~~~~~~~~~~~~~~~~~~~

    - Review: how much measuring do I really need to do for a frame.Drawing when I can scale vector graphics on demand?
      At minimum I need to respect requested sizes and anchor point positioning.
    - Review: look at how a proposed Maybe type would work to get rid of zero-valued defaults in :python:`frame.Drawing`

visual/frame/empty_space.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: consider some kind of text client services mixin to get rid of the "text" property on :python:`frame.EmptySpace`.
      That property only exists to allow me to inject empty spaces into a sequence of `FormattedText` instances without having to special case
      the processing loop. Abstracting this expediency to a mixin would make it "intentional design" instead of "an ugly hack".

        - Suggests that a RenderingFrame implementation could expose a do-nothing "Impersonator" mixin.
          :python:`EmptyTextSpace(EmptySpace, FormattedText.Impersonator)` (check ordering!)
        - This is an interesting concept for blending capabilities. Worth exploring.

    - Nomenclature: The :python:`frame.EmptySpace` initializer should  have requested_size parameter, not size, for consistency.
    - Factor: can I remove :python:`frame.EmptySpace.draw` and let the `SimpleElement` base class handle it? That's its job.

visual/frame/formatted_text.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor: decouple the formatted text content from the ReportLab rendering technology
    - Factor: figure out a way to remove :python:`frame.FormattedText.height_extra` to a global "rounding pad" in settings.
      Does this padding belong more appropriately in the geometry?
    - Review: `FormattedText.measure` has another use case for baked-in constraints on the Distance type.
    - Review: the semantics around passing the extent to :python:`RenderingFrame.measure` seem inconsistent.

        - look more closely at how extent is used in the `measure` methods in `FormattedText`, `Drawing`, `Container`, and `SimpleElement`.

    - Factor: casting Sequence[Flowable] to list[Flowable] in :python:`FormattedText.draw` speaks to a lack of design planning.
      correct the underlying types.

visual/frame/page_rule.py
~~~~~~~~~~~~~~~~~~~~~~~~~

    - Nomenclature: The :python:`frame.HorizontalRule` initializer should  have requested_size parameter, not size, for consistency.
    - Review: why does :python:`frame.HorizontalRule` have a measure() method instead of letting `SimpleElement` do the work?

visual/frame/stack_layout.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Nomenclature: are :python:`StackLayoutStrategy.get_stack_pos` & :python:`StackLayoutStrategy.get_other_pos misnamed`?
      Use `get_{stack|other}_idx` instead?
    - Review: do I need options to the `StackLayoutStrategy` initializer for inter-element spacing?
    - Review: is it appropriate to throw a `RegionOverflow` exception up to :python:`StackLayoutStrategy.layout`'s caller?
      It seems icky to me to misuse an exception on a normal execution case that could be handled by a boolean "clip" setting in the
      `LayoutStrategy` protocol.  OTOH, Python idiom encourages this approach.  Hybrid?  When no "clip" setting, raise an exception?
      There's peril there: don't over-complicate the interface with implicit behaviors.
    - Review: note that whenever content isn't clipped by `layout`, I'll be getting an implict z-order imposed by the order in which I draw
      the frames where later ones overwrite earlier ones; which could raise some interesting apparent bugs on output consistency.
    - Factor: horizontal/vertical helper methods + associated direction enum should be exposed as a mix-in so anybody can use them
    - Review: :python:`StackLayoutStrategy.layout` has explicit coordinate system assumptions about origin placement and axis direction
    - Review: is disregarding frames with any zero dimensions in :python:`StackLayoutStrategy.layout` appropriate? What are the unintended
      consequences of doing this?

visual/frame/layout/distance.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: check usage of :python:`layout.distance.DistanceUnit` - am I dupliating work already in enum.StrEnum?

        - particularly with the :python:`layout.distance.unit_str` dictionary

    - Factor: :python:`Distance.MeasureType` needs to support ConvertibleToFloat if it doesn't already
    - Factor: should :python:`Distance.MeasureType` be a Generic type parameter?
    - Factor: make :python:`Distance.fit_to`, :python:`Distance.zero`, and :python:`Distance.infinite` into immutable `Singleton` instances.
    - Review: `Distance` should have a property for it's default __str__ (et al) format - sig figs, fraction, digits etc.  How does numpy do this?

        - it strikes me that I should able to do this an overridable style in the new Styles model.

    - Factor: pull out the magic distance value regexp from :python:`Distance.parse` to a class property.
    - Review: stretchy (unit == '*') handling in :python:`Distance.__lt__` et al looks sketchy/incomplete.
    - Review: is the Numeric library any use to me for distances and :python:`Distance.MeasureType`?
      `numeric` has always been unpleasant to use because it's so poorly typed, but maybe I'll get lucky here.
    - Factor: can I unify the code in :python:`Distance.__eq__` and :python:`Distance.__lt__` w.r.t their match strategy?

visual/frame/layout/region.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Add: I can floordiv by another extent to produce a pure number - same story on truediv
    - Review: the `Region.__contains__` operator says it works in absolute coordinates - I have doubt.
      There's some real consistency/coherency issues to resolve about what 'containment' means for region-in-region or point-in-region w.r.t
      aboslute or relative coordinates
    - Review: `Region.__contains__` is one among many operators across `Region`, `Pos`, `Extent` that make strongly
      assumpition about the coordinate vector orientations (and probably handedness if we add a 3rd dimension).
      These operators will make the canonical use case for abstracting coordinate system transforms to a combinator layer.
    - Review: look at `Region.bounds` |rarr| this method is doing "unit propagation" as outlined in the proposed data forwarding feature.

reports/controller.py
~~~~~~~~~~~~~~~~~~~~~

    - Review: the `PageController` protocol asks for a lot of data: can it do more with less? Is it all necessary?
    - Review: `RenderingFrame.state` flags overlap with the `RenderingFrame.begin_page` return value.  Can I clean this up?
    - Defect: `PageController.begin_page` only asks the active layout if there is more data on the `self.page.begin_page(page_number)` call.
      Other layouts may have child frames that still have something to say!
    - Factor: is `PageController.begin_page` the correct place to make the calls `Page.measure` and `Page.do_layout`? Think on it.

reports/kanji_summary/document.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor: decouple ReportLab technology from the `kanji_summary.document.KanjiReportData` class.
    - Review: how is `RenderingFrame.requested_size` being used in the various implementations - is it clean/consistent?
    - Rename: DrawingForRL to "SupportsReportLab[P]" where P is a protocol? Remember, generics are not real types in Python like in C++.
    - Add: some kind of fallback (to say text) if `kanji_summary.document.KanjiReportData.get_glyph_svg_drawing` can't get an SVG drawing.
      I would need a similar text glyph fallback for radicals, too.
    - Review: other fallback situations - say KanjiSVG for dict2 when looking at radicals?
    - Review: perhaps a partial appliction wrapper around `glyph_svg.draw_glyph` to make draw_radical in
      `kanji_summary.document.KanjiReportData.get_radical_svg_drawing`?
    - Review: a full-sized version of the radical drawing in `kanji_summary.document.KanjiReportData.get_radical_svg_drawing` instead of drawing
      the glyph w/ the non-radical strokes invisible?
    - Review: consider "no orphan" `FormattedText` rendering frames? Or should this be a style? Look at the use case in the kanji defintions
      body text in `kanji_summary.document.KanjiReportData.format_body_text`.
    - Factor: eliminte the `size` parameter to `kanji_summary.document.build_data_object`. The `Drawing` frame should supply it.
      See notes about `size` parameters in `external_data.kanji_svg.KanjiSVG.draw_stroke_steps` et al.
    - Factor: the style needs to be in options, not hardcoded, in `kanji_summary.document.build_data_object`
    - Big Issue: reconcile a big block of details from KanjiDict against multiple entries in KanjiDict2.
      `kanji_summary.document.build_data_object` only takes the _first_ from zip_longest(kanji_details, radical_details).

reports/kanji_summary/kanji_summary.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor: replace most of kanji_summary.kanji_summary.KanjiSummary with `EmptySpace` frames to do padding and put
      all of the child text into `FormattedText` frames all wrapped in a vertically stacked `Container` frame.
    - Review: the parent `SimpleElement` class owns the `_requested_size` data. Touching this private parent data during
      `KanjiSummary.__init__` is a faux pas. Consider a forwarding property whose setting passes the data up to the parent.
      See the notes about aliasing and forwarding for `DelegatingRenderingFrame`.
    - Factor: put attribute attrgetters onto the geometry classes to replace the ones in `KanjiSummary.measure` for FP convenience
    - Factor: use my coalesce helpers for distance instead of 'or None'
    - Doc: is the `sd_infosheet_dynamic_layout` Mermaid diagram in :python:`kanji_summary.report.Report` in the wrong spot?
      Generalize it and put that with `PaginatedReport`?
    - Doc: the `fc_infosheet_generate` Mermaid diagram in :python:`kanji_summary.report.generate` is also releveant to `PaginatedReport`.
      Move it or copy a generalized version.
    - Review: :python:`kanji_summary.report.Report.get_page_layout` is not very robust - needs a review of the possible failure
      modes and appropriate error handling.

        - Same story for :python:`kanji_summary.report.generate` - what about unrecognized kanji input (ie a "no data" case)?

    - Review: a nice-to-have is multiple kanji in one report with practice sheets interleaved.
      See the dev note about the "Report chaining" features - seems a logical place to do this.

reports/kanji_summary/radical_summary.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Factor: convert `RadicalSummary` to be a vanilla horizontally stretchy vertical stack with a minimum size to fit the radical's SVG drawing.
      I don't need to have a customized layout.

reports/practice_sheet (entire package)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Review: is this worth doing |rarr| :python:`lazy(function_call())` that only executes the call if it absolutely has to.

        - :python:`lazy(iterable[function_call])` ?? or maybe:  :python:`call_on_demand(...)`

    - Review: better nomenclature for `DrawingForRL` & `RLDrawing`
    - Review: handle page settings overrides in the page factory-fetcher as passed-in styles
    - Add: I need a database for kana - borrow heavily from Wiktionary -- see experiments.ipynb for REST queries
    - Review: nomenclature in :python:`adapter.svg`:

        - See aslso the "Rendering technology agnostic" feature  notes.
        - `DrawingForRL` |rarr| :python:`adapter.fromSVG.toRL.Drawing`?
        - `RLDrawing` |rarr| :python:`adapter.fromRL.toSVG.Drawing`?
        - A more type algebra naming with specialized backing objects like :python:`Drawing[<from>][<to>]` ?

    - Review: :python:`practice_sheet.document.PracticeSheetData` initializer could be more robust. Consider all the failure modes in the math and
      allocating resources.  Similar robustness considerations for `practice_sheet.document.build_data_object`
    - Review: the `Practice Sheet` uses hard coded distances for spacing -- figure out a better way using config params or an automatic strategy
