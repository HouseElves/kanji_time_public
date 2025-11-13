# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Contain all Kanji Time report implementations.

Each distinct Kanji Time report has a subpackage in 'reports' with the same name as its report alias.

All reports are defined by subpackages for the Kanji Time report module subject to the constraints below:

    #) A report subpackage must contain a class named `Report` in a module named `report.py`.
    #) The `Report` class must expose a mechanism to obtain and represent its initial data set via the `gather_report_data` method and `Data` type declaration.
    #) The `Report` class must also expose its preferred output file name that is unique to its initialization parameters.

In the vast majority of Kanji Time reporting use cases, a particular `Report` class obtains a simple pagination controller by deriving from :class:`controller.PaginatedReport`.

    - The direct advantage of using this controller is that it frees the report to focus on data management and binding data to its rendering frames as needed.
    - The report instance does *not* have to handle details of page layout and page breaks unless it wants exceptional behavior.
      Even then, it only needs to handle those exceptions ad hoc.
    - The parent PaginatedReport class handles all the typical layout and pagination cases itself.

There are two reports currently defined:

    **kanji_summary**
        a dictionary information for a particular kanji

    **practice_sheet**
        stroke-order diagram and ruled practice areas for a particular kanji

.. only:: dev_notes

    TODO:  I need a "seealso" to the relevant design doc pages.


Pagination Controller Modules
-----------------------------

.. toctree::
   :maxdepth: 1
   :caption: Pagination Control

   controller.py <controller.py>


Kanji Time Packaged Report Modules
----------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Defined Reports

   Kanji Summary <kanji_summary/__init__.py>
   Practice Sheet <practice_sheet/__init__.py>


"""

