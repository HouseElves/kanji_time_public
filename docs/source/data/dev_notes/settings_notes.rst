.. _external_data.settings.py.dev_notes:

===========================================
external_data/settings.py Development Notes
===========================================

For: :mod:`external_data.settings`

.. include:: /common


New Features
------------

YAML Settings
~~~~~~~~~~~~~

    - Move all user-configurable options to a YAML (or YAML-like) document
    - Need to include help strings, preferably baked right into a setting schema-like object


Code Review/Adjustments
-----------------------

    - Review: can I do better for the `external_data.settings.project_root` string and use a stdpath.Path?
      `project_root` is specifically for Sphinx so it's a little less whiney.

        - is `project_root` even in the correct settings module?



