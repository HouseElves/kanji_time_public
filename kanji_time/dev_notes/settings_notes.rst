:orphan:

.. _settings.py.dev_notes:

===============================
settings.py Development Notes
===============================

For: :mod:`settings`

.. include:: /common

New Features
------------

YAML Settings
~~~~~~~~~~~~~

    - Move all user-configurable options to a YAML (or YAML-like) document
    - Need to include help strings, preferably baked right into a setting schema-like object


Code Review/Adjustments
-----------------------

    - Review: avoid using strings directly on file system locations.
      This may not be 100% possible because of 3rd party technology limitations.
      I.e. ReportLab does not play well with pathlib.Path instances.


