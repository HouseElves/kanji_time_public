.. include:: /common

===============
Reports Package
===============

All reports are defined by subpackages for the |KT| report module subject to the constraints below:

    #) A report subpackage must contain a class named `Report` in a module named `report.py`.
    #) The `Report` class must expose a mechanism to obtain and represent its initial data set via the `gather_report_data` method and `Data` type declaration.
    #) The `Report` class must also expose its preferred output file name that is unique to its initialization parameters.

In the vast majority of |KT| reporting use cases, a particular `Report` class obtains a simple pagination controller by deriving from :class:`controller.PaginatedReport`.

    - The direct advantage of using this controller is that it frees the report to focus on data management and binding data to its rendering frames as needed.
    - The report instance does *not* have to handle details of page layout and page breaks unless it wants exceptional behavior.
      Even then, it only needs to handle those exceptions ad hoc.
    - The parent PaginatedReport class handles all the typical layout and pagination cases itself.

TODO:  I need a "seealso" to the relevant design doc pages.


Pagination Controller Modules
-----------------------------

    .. toctree::
       :maxdepth: 1
       
       __init__.py
       controller.py


|KT| Packaged Report Modules
----------------------------

    .. toctree::
       :maxdepth: 2

       kanji_summary/index
       practice_sheet/index

   
   
