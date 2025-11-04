:orphan:

.. kanji_time-reports-practice_sheet-py-dev_notes:

=======================================
Practice Sheet Report Development Notes
=======================================

For: :mod:`kanji_time.reports.practice_sheet`

.. include:: /common

Thread Safety (for a multithreaded future)
------------------------------------------

    - Review :python:`practice_sheet.document.PracticeSheetData` for thread safety issues.

Future Feature Adds
-------------------

Layouts
~~~~~~~

    - a "replicate" container would be really useful:  ContentFrame + # times + a layout strategy

        - the canonical use case is a grid:  replicate this FormattedText frame 20 times and apply a 5x4 grid layout strategy.
        - whether or not there's actually 25 instances or a single "sliding" instance that cycles data in/out for each cell is an
          implementation detail - the important point is that it should *look* to the client that there's 25 distinct instances.

    - headers/footers would also be useful

        - maybe a specialized container for out-of-margin content like headers/footers or even margin notes, revision marks, and line symbols.
        - one header and one footer instance shared by all Page instances in a report (unless there's an override)
        - there's probably enough hooks in the :python:`PageController` protocol to make this work.  If not, add them.

Whitespace strategies
~~~~~~~~~~~~~~~~~~~~~

    - The anchor point semantic isn't really well defined.

        - Am I positioning inside the host container or inside the frame?
        - The code seems to take both points of view in different places - drawings vs flowing text.

    - The hardcoded spacing between `Practice Sheet` elements is another code case for rethinking the whitespace handling.

Code Review/Adjustments
-----------------------

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



