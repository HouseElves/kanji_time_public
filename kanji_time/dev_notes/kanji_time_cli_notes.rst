:orphan:

.. _kanji_time_cli.py.dev_notes:

===================================
kanji_time_cli.py Development Notes
===================================

For: :mod:`kanji_time`

.. include:: /common

Security
--------
    - I need think about penetration testing and ways to secure the report add-on process for third-party contributions
    - What precautions do I need to take against loading malicious code with LoadModule?


New Features
------------


Report chaining
~~~~~~~~~~~~~~~

    - Define meta-reports that can chain or interleave pages (possibly conditionally) different reports into one big reporting job.
    - The prototype use case is the processing multiple kanji in one Kanji Summary report which also interleaves Practice Sheets:
      this output should all land in one big happy PDF as a themed workbook with an theme description page.

        - Oh! That "themed workbook" makes this concept smell like a 'report binder' feature.
        - All the functionality there with different `Page` instances controlling different page layouts, it's just a question of wrapping
          a driver mechanism around it.
        - The back end isn't hard at all, I think passing the same surface through everybody is the key part then delegating to the correct
          report on each page.  Good thing that I have a delegation infrastructure in place :D.
        - The front-end UX? Well, that's deferred just like it is for everything else. We'll hard code instances as needed for now.


Rendering technology agnostic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - This feature is shaping up to be a domain-specific language
    - make init_reportlab() part of the technology abstraction & adapter layer by replacing it with a generic technology initialization
    - make a generic display surface provider = :code:`DisplaySurface` is a cheap subclassing stunt to alias ReportLab's canvas
    - make a data formats conversion protocol for technologies, for example

        - this is a customer converter from an Extent to ReportLab's version as a tuple of two floats:

            :python:`page_size = tuple(map(lambda x: x.pt, page_settings.page_size))`

    - going to need some file system handling protocols: ReportLab barfs on pathlib.Path, what other Python conveniences are sketchy?
    - make a generic page-eject - `display_surface.showPage` is ReportLab-specific


Customization
~~~~~~~~~~~~~

    - Make the reporting package path a configurable option. We're half way there with the alias |rarr| module map in VALID_REPORTS


Code Review/Adjustments
-----------------------

    - Review: add the page's settings to a `PageController` property?
    - Review: there's overlapping functionality with `begin_page() == True` and `States.have_more_data`
    - Add short/long help string properties to the report implementation's `Report` class for use in the CLI --help=<report_alias>.
    - Make a more robust command dispatch model that consumes an argparse.Namespace and produces a Command instance of some kind.
    - Make failure cases funnel into a common error exit function that imposes consistent failure reporting strings and formats.
    - Define and document a set of exit codes for bash scripting: current codes are already in the Sphinx .RST tree
    - Factor: package all the ReportClass validation into one happy little function in :python:`kanji_time.execute_report`...
      perhaps even make a "ReportPlugIn" protocol, even?

