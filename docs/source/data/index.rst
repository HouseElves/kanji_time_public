.. _external_data-dev_guide:

External Data Sources
=====================

Kanji Time uses well-known & trusted Open Source data for the kanji information that it presents.
See :ref:`open_source_data` for full details about these datasets.

The Kanji Time :code:`external_data` module encapsulates all the interfaces into these datasets.
The design isolates each dataset into its own dedicated code module, linked below.

.. toctree::
   :maxdepth: 1

   kanji_dict
   kanjidict2
   kanji_svg
   radicals
