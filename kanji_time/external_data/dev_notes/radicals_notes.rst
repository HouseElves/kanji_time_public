:orphan:


.. _radicals.py.dev_notes:

=============================
radicals.py Development Notes
=============================

For: :mod:`external_data.radicals`

.. include:: /common


Performance
-----------

    - the `external_data.radicals.radical_map` and `external_data.radicals.meaning_map` trigger a lot of start-up time activity.
      Rethink this entire mechanism with better awareness of my dependencies and what can be deferred.

        - `external_data.radicals.Radical.__new__` looks like the offender in this process, but this is just the guy that kicks off the start-up issues.
        - Is it worth adding some visual feedback with a progress bar?

Thread Safety (for a multithreaded future)
------------------------------------------

    - the interaction between `external_data.radicals.radical_map`, `external_data.radicals.meaning_map`, and `external_data.radicals.Radical.__new__`
      touches a vast amount of global data.  I need to lock everything down until the load completes.

New Features
------------


Extended Radical Data
~~~~~~~~~~~~~~~~~~~~~

    - Flesh out radical information with new sources giving some better etymology and history


Code Review/Adjustments
-----------------------

    - nada!
