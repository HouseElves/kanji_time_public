# kanji_time_cli.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Implement the kanji_time CLI entry point.

This is a highly enhanced version of a ChatGPT generated baseline.

.. seealso:: :ref:`kanji_time_gpt` for the original LLM output.

The command line is intentionally simple.  We use the standard argparse library to handle input arguments according this protocol:

.. code-block::

    --report= / -r ==> the report to generate
    --output_dir= / -o ==> the destination directory for the PDF output files
    --help / -h ==> command line argument help
    --help=<report name> ==> help specific to the the <report_name> report.

Each report has an entry point that lives in its own subpackage of the `reports` package in the (aptly called) module `report.py`.
Currently there are only two report sub-packages: 'kanji_summary' and 'practice_sheet'.

The `execute` function in this module is the heart of report generation.

    - It loads a report entry point from a whitelisted report module then enters a page-pump loop to produce the report output.
    - This page-pump interacts with the report via the well-known `ReportingFrame` and `PageController` protocols.

*Any entry point that obeys the rules of the reporting protocol contract can be invoked as a report*.

.. rubric:: Reporting Protocol Rules
    :heading-level: 2

These three rules define the reporting protocol contract.

    1. The `report.py` module for the report contains a class definition named `Report` that implements both the ReportingFrame and
       PageController Python protocols.
    2. This Report class has additional class-level symbols `Data` and `gather_report_data` for acquiring report-specific data.
    3. There is an instance method that produces a file name unique to the report *and* a kanji glyph.

The page-pump in `execute` interacts with report via the protocol rules in roughly a Template Method pattern (see [GoF]_, pg 325)

.. rubric:: Whitelisting Reports
    :heading-level: 2

To help in blocking malicious code injection, kanji_time only runs registered well-known reports.

.. only:: dev_notes

    - I need think about penetration testing and ways to secure the report add-on process for third-party contributions

The `VALID_REPORTS` report registry maps the command-line report alias to the full module name of its report entry point is as below.

===================  =============================
Report Alias         Report Module
===================  =============================
kanji_summary        reports.kanji_summary.report
practice_sheet       reports.practice_sheet.report
===================  =============================

.. only:: dev_notes

    .. seealso:: :doc:`dev_notes/kanji_time_cli_notes`

----

"""
import argparse
import importlib
import logging
import pathlib
import sys
from types import ModuleType


from typing import cast

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab import rl_config

from kanji_time.visual.protocol.content import DisplaySurface, States
from kanji_time.utilities.general import log, pdf_canvas as open_surface

# pylint: disable=wrong-import-order,wrong-import-position
import logging
logger = logging.getLogger(__name__)


# Globals ---------------------------------------------------------------------------------------------------------------------------------- #


# Safe Report Registry
VALID_REPORTS = {
    "practice_sheet": "kanji_time.reports.practice_sheet.report",
    "kanji_summary": "kanji_time.reports.kanji_summary.report"
}


# Report Generation Entrypoint ------------------------------------------------------------------------------------------------------------- #


def init_reportlab():
    """
    Make ReportLab ready to receive our output.

    The technology-specific global initialization entry point for ReportLab.

        - we need a Unicode font supporting kanji glyphs.
        - we're being forgiving about boundary checking on tables.

    .. only:: dev_notes

        - make this function  part of the technology abstraction & adapter layer.

    :return: None.
    """
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
    rl_config.allowTableBoundsErrors = True


def load_report_module(report_alias: str) -> ModuleType:
    """
    Load the implementation of <report_alias>.

    We're assuming that the code we're looking for lives in `reports.<report_alias>.report`.

    The `VALID_REPORTS` dictionary is a first cut at protecting against malicious code injection by registering known report aliases that
    point to well-known modules.

    :param report_alias: the report for which we are loading code, this must be a well-known value to KanjiTime.
    :return: the Python module containing the <report_alias>'s implementation.

    .. only:: dev_notes

        - Make the reporting package path a configurable option. We're half way there with the alias -> module map in VALID_REPORTS
        - Beef up the precautions against malicious code around loading modules

    """

    module_path = VALID_REPORTS[report_alias.strip()]
    try:
        logger.info(f"importing '{report_alias}' from '{module_path}'")
        m = importlib.import_module(module_path)
        logger.info(f"successfully imported '{report_alias}' from '{module_path}'")
        return m
    except ModuleNotFoundError as e:
        print(f"Report implementation missing for '{report_alias}' ({module_path})", file=sys.stderr)
        logger.error(f"Could not find module '{module_path}': {e}")
    except TypeError as e:
        print(f"Report implementation for '{report_alias}' ({module_path}) is  not a package: {e}.", file=sys.stderr)
    except Exception as e:
        print(f"Internal error for '{report_alias}' ({module_path})", file=sys.stderr)
        logger.error(f"Unknown error loading '{module_path}': {e}")

    print(f"Failed to import report '{report_alias}' ({module_path})", file=sys.stderr)
    sys.exit(1)


def execute_report(report_alias: str, glyphs: str, target_dir: pathlib.Path):
    """
    Run <report_alias> for <glyphs> with output(s) directed to <target_dir>.

    We're running a simple pagination loop against a `RenderingFrame + PageController` client.
    We're also explicitly separating data acquisition from data presentation even though the client is responsible for both activities.
    This separation gives us better process control to support later growth of the system with simultaneous jobs, asynchrony, background
    processing, and data reuse,

    The client code that implements the report lives in the module `reports.<report_alias>.report`.

    We assume that
        1. there is a type with RenderingFrame and PageController behaviors, named Report, defined in that module,
        2. the Report type exposes subtype called `Data` that acts as the reports data source,
        3. the Report type implements a function `gather_report_data` that populates a `Data` instance for the report, and,
        4. the Report type exposes an `output_file` property for output unique to the report and the glyph.

    Once we acquire the report data, we can create a `Report` type instance on those data and proceed with the output.

    :param report_alias: the name of module in `reports` containing the report generator
    :param glyphs: the kanji glyphs on which we're reporting
    :param target_dir: the os path to receive the output files.

    :raises ValueError: if any of the report module assumptions are incorrect for <report_alias>.

    Class Interactions
    ------------------

    The below sequence diagram illustrates the interactions in running a report.

    .. mermaid::
        :name: sd_report
        :caption: Sequence diagram for generating a report.

        ---
        config:
            layout: elk
            class:
                hideEmptyMembersBox: true
        ---
        sequenceDiagram
            participant CLI as CLI (kanji_time.py)
            participant R as Report (e.g. KanjiReport)
            participant D as Report.Data
            participant P as PageController
            participant PDF as DisplaySurface

            CLI->>CLI: parse args
            CLI->>R: gather_report_data(glyph)
            R->>D: build data object
            CLI->>R: initialize report
            loop per glyph
                CLI->>R: begin_page(n)
                R->>P: layout_name + layout
                P->>PDF: draw(page)
                PDF->>PDF: showPage()
                CLI->>R: check report.state
            end

    .. role:: python(code)
        :language: python

    .. only:: dev_notes

        - Isolate technology specific operations to the not-yet-coded technology abstraction layer:

            - generic technology initialization replacing `init_reportlab`
            - generic display surface provider = :code:`DisplaySurface` is a cheap subclassing stunt to ReportLab's canvas
            - data formats conversion protocol for technologies, for example

                - this is a customer converter from an Extent to ReportLab's version:

                    :python:`page_size = tuple(map(lambda x: x.pt, page_settings.page_size))`

                - file system handling: ReportLab barfs on pathlib.Path

            - generic page-eject - `display_surface.showPage` is ReportLab-specific

        - Meta-reports that can chaining (possibly conditionally) different reports into one big reporting job
        - Review: add the page's settings to a `PageController` property?
        - Review: overlapping functionality with `begin_page() == True` and `States.have_more_data`
        - Factor: package all the ReportClass validation into one happy little function... perhaps a Protocol, even?

    ----

    """
    init_reportlab()

    # Let's get our report code.  We'll enforce our assumptions on it for sanity.
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

    # Main event.  Generate one report for each glyph in the glyph set.
    #
    # Report chaining would land in this too.
    print(f"Beginning {report_alias}.")
    for glyph in ''.join(glyphs):
        # Issue: skip glyphs that are not in scope -> avoid an "SVG not found" error later on... meh, here is not the right place to do this.
        print(f"Processing {glyph}...on page...", end="")
        logging.info("Processing %s", glyph)

        data = report_module.Report.gather_report_data(glyph)
        report_generator = report_module.Report(data)
        page_settings = report_generator.page_factory.settings
        page_size = tuple(map(lambda x: x.pt, page_settings.page_size))
        full_path = str(target_dir / report_generator.output_file)  # NOTE:  ReportLab doesn't like Path objects - we must pass a string.

        with open_surface(full_path, pagesize=page_size) as display_surface:
            page_number = 1
            while report_generator.begin_page(page_number):
                print(f"{page_number}...", end="")
                report_generator.draw(cast(DisplaySurface, display_surface), page_settings.printable_region)
                display_surface.showPage()  # this is a ReportLab-specific idiom - should be generic
                if States.have_more_data not in report_generator.state:  # make a bool property instead? Dupes begin_page()'s return value?
                    break
                page_number += 1
        print(f"done! PDF result in {full_path}")

    print(f"{report_alias} complete.")


# Help Subsystem --------------------------------------------------------------------------------------------------------------------------- #


def show_report_help(report_alias: str):
    """
    Send help text about the <report_alias> report to the standard output stream.

    :param report_alias: the report about which we want help text.
    :return: None
    :raises: ValueError if we don't find any help text.

    .. only:: dev_notes

        - Add short/long help string properties to the report implementation's `Report` class.

    """
    module_path = VALID_REPORTS[report_alias]
    try:
        module = importlib.import_module(module_path)
        help_text = getattr(module, "__doc__", None)  # should be obtained from the Report first then fall back to her
        print(help_text.strip() if help_text else f"No docstring found for report '{report_alias}'.")
    except Exception as e:
        print(f"Failed to load report help for '{report_alias}': {e}", file=sys.stderr)
        raise ValueError(f"Failed to load report help for '{report_alias}'") from e


# Entry Point Logic ------------------------------------------------------------------------------------------------------------------------ #


def cli_entry_point():
    """
    Parse and dispatch command line requests.

    :return: None

    .. only:: dev_notes

        - This function started life in ChatGPT 4o's dark little heart. Convert it to a more robust command dispatch model from a Namespace.
        - Define and document a set of exit codes for bash scripting: current codes are already in the Sphinx .RST tree
        - Create a common error exit function with consistent failure reporting.

    """

    parser = argparse.ArgumentParser(
        prog="kanji_time",
        description="Generate kanji practice sheets and kanji dictionary information in PDFs."
    )

    parser.add_argument(
        "kanji",
        nargs="+",
        help="One or more kanji glyphs for which to generate reports."
    )

    parser.add_argument(
        "--report", "-r",
        choices=VALID_REPORTS.keys(),
        help="Select the report to generate.",
        action='append',
    )

    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Directory to output generated PDF files."
    )

    parser.add_argument(
        "--help-report",
        metavar="REPORT",
        choices=VALID_REPORTS.keys(),
        help="Show help for a specific report module."
    )

    args = parser.parse_args()

    # here is where I would insert a real Namespace -> Command dispatch function and eliminate these three distinct code paths.

    # Deal with help requests
    try:
        if args.help_report:
            show_report_help(args.help_report)  # this converts all exceptions to a ValueError
            return
    except ValueError:
        print("kanji_time ended abnormally.", file=sys.stderr)
        sys.exit(1)  # should be a well known and documented named constant

    # Set up the output paths
    try:
        output_dir = pathlib.Path(args.output_dir.strip())
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # need  common failure / abort function - incorporate in the the dispatcher
        print(f"Unable to send report output to {args.output_dir}: {e}", file=sys.stderr)
        print("kanji_time ended abnormally.")
        sys.exit(2)  # should be a well known and documented named constant

    # Now let's do the report.  The logger will handle exceptions on our behalf.
    if args.report is None:
        print("No Kanji Time report requested.  Exiting.")
        sys.exit(2)
    for report_alias in args.report:
        if report_alias not in VALID_REPORTS:
            print(f"{report_alias} is not a known Kanji Time report.")
            sys.exit(2)
        log_file = output_dir / f"{report_alias}.log"
        with log(log_file, logging.INFO):
            execute_report(report_alias, args.kanji, output_dir)


if __name__ == "__main__":
    cli_entry_point()
