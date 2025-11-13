.. _addon_model:

How Does the Report Add-on Model Work?
======================================

Kanji Time exploits Python's dynamic code loading capabilities via the `LoadModule` function to bring specific report generator logic to bear on demand.

Each Kanji Time report has a well-known command line alias that also names a subpackage of `reports` that contains its supporting code objects.
E.g. the `reports.kanji_summary` package contains all the code objects necessary to run the "kanji_summary" report.

Since running arbitrary code from the command line is a security breach, each report alias must also be present in Kanji Time's report whitelist table :data:`kanji_time.VALID_REPORTS`.

.. rubric:: Report Add-on Model Contents
    :heading-level: 2

- :ref:`addon_contract`
- :ref:`contract_enforcement`
- :ref:`contract_action`

----

.. _addon_contract:

The Report Add-on Contract
--------------------------

A report provider creates a Python package that fulfils a simple contract around the existence of certain special symbols in order for Kanji Time to call into the report's code.

Put reporting packages in Kanji Time's :mod:`reports` package as a subpackage with the same name as the report alias.
(At some point in the future there will be an automated "add a report to Kanji Time" process.)

The report package must contain module named `report.py` that contains all of the following:

#. a data type, `Report`, that implements the :class:`RenderingFrame` and :class:`PageController` behaviors
#. an opaque data type, `Report.Data`, that is an alias for the source data type accepted by the `Report` class initializer,
#. a function `Report.gather_report_data` that creates and populates an instance of `Report.Data`, and,
#. a string property `output_file` that is an output file name unique to the report alias and a kanji glyph.

This contract is very rough and still under development.

    - It may change subtly in the next development round.
    - Future plans include enforcing it by a Python protocol.

.. seealso::

    - Kanji Summary report module :mod:`reports.kanji_summary.report`
    - Practice Sheet report module :mod:`reports.practice_sheet.report`

Back to :ref:`addon_model`

----

.. _contract_enforcement:

Contract Enforcement
--------------------

Enforcing the Add-on Contract is very primitive right now.
The enforcement algorithm uses a simple sequence of attribute checks:

.. code-block:: python
   :caption: Enforcing the Add-on Contract
   :linenos:

    report_module = load_report_module(report_alias)
    ReportClass = getattr(report_module, "Report", None)  # pylint: disable=invalid-name
    if not ReportClass:
        raise ValueError(f"Module '{report_alias}' does not define a 'Report' class.")
    if not hasattr(ReportClass, "Data"):
        raise ValueError(f"Report class in '{report_alias}' is missing a 'Data' type.")
    if not hasattr(ReportClass, "gather_report_data"):
        raise ValueError(f"Report class in '{report_alias}' is missing a 'gather_report_data' function.")
    if not hasattr(ReportClass, "output_file"):
        raise ValueError(f"Report class in '{report_alias}' is missing an 'output_file' property.")

.. seealso:: The above code in context in :func:`kanji_time.execute_report`

Back to :ref:`addon_model`

----

.. _contract_action:

Acting on the Add-on Contract
-----------------------------

The most important aspect of the Add-on contract is to give a standard location for finding a report's code and data.

:func:`kanji_time.execute_report` separates the actions of loading initial data and instantiating the report generator.
This is with an eye to the future of possibly sending a lengthy data access off into the background while attending to other tasks.

The key player once we've loaded data and bound it to the report is the report's implementation of PageController.

:class:`reports.controller.PageController`

    This protocol defines the behavior for generating any paginated report.
    It lets reports define different layouts based on a page type (say summary vs detail pages) and allows reports to populate their layouts with data on a per-page basis.

There is a lot going on in a page controller.  So much that Kanji Time provides a solid implementation of the protocol in the form of a mixin.

:class:`PaginatedReport`

    This mix-in provides a typical implementation of the `PageController` logic, including page state management, layout switching, and lazy instantiation of page containers.


These players drive the pagination loop in the below code as shown in the sequence diagram at :ref:`sd_pagination`.
Most of this loop isn't central to understanding the Add-on Contract.
For that understanding, let's examine lines 1, 2, 9, and 11.

.. code-block:: python
    :caption: a pagination loop
    :linenos:

        data = report_module.Report.gather_report_data(glyph)
        report_generator = report_module.Report(data)
        page_settings = report_generator.page_factory.settings
        page_size = tuple(map(lambda x: x.pt, page_settings.page_size))
        full_path = str(target_dir / report_generator.output_file)

        with open_surface(full_path, pagesize=page_size) as display_surface:
            page_number = 1
            while report_generator.begin_page(page_number):
                print(f"{page_number}...", end="")
                report_generator.draw(cast(DisplaySurface, display_surface), page_settings.printable_region)
                display_surface.showPage()  # this is a ReportLab-specific idiom
                if States.have_more_data not in report_generator.state:
                    break
                page_number += 1
        print(f"done! PDF result in {full_path}")

- **lines 1 & 2** show the separation of data acquisition and instantiating the report generator
- **line 9** shows a call to `begin_page`, which is a method of the :class:`PageController`.
  This call back informs the report that it's time to get all its content frames positioned and bound to data so that we can draw the page on **line 11**.

.. seealso:: The above code in context in :func:`kanji_time.execute_report`

Back to :ref:`addon_model`

