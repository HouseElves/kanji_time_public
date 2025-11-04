:orphan:

.. kanji_time-reports-controller-py-dev_notes:

===============================
controller.py Development Notes
===============================

For: :mod:`kanji_time.reports..controller`

.. include:: /common


Future Feature Adds
-------------------


Pagination Enhancements
~~~~~~~~~~~~~~~~~~~~~~~

    - Instantiate a `PaginatedReport` with keyword arguments for the various layouts attached to a dict of `RenderingFrame` instances
      for content?
    - `PageController.begin_page` returning `None` is a bit clumsy for "no page" when coupled to the overlap with the state flags.


Code Review/Adjustments
-----------------------
    - Review: the `PageController` protocol asks for a lot of data: can it do more with less? Is it all necessary?
    - Review: `RenderingFrame.state` flags overlap with the `RenderingFrame.begin_page` return value.  Can I clean this up?
    - Defect: `PageController.begin_page` only asks the active layout if there is more data on the `self.page.begin_page(page_number)` call.
      Other layouts may have child frames that still have something to say!
    - Factor: is `PageController.begin_page` the correct place to make the calls `Page.measure` and `Page.do_layout`? Think on it.

