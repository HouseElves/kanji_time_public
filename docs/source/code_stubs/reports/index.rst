===============
Reports Package
===============

.. automodule:: kanji_time.reports.__init__

Top Level Code
--------------

A report subpackage must contain a class named `Report` in a module named `report.py`.
The Report class will typically derive from :class:`controller.PaginatedReport` to get a simple pagination loop.
All the report has to do is manage its data and bind it to rendering frames in its presentation.

.. toctree::
   :maxdepth: 1

   __init__.py
   controller.py

Indvidual Report Subpackages
----------------------------

.. toctree::
   :maxdepth: 1

   kanji_summary/index
   practice_sheet/index
