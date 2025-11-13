:orphan:

.. _kanji_time_gpt:

ChatGPT 4o Baseline: kanji_time_cli.py
======================================

The final version of kanji_time_cli.py is a heavily modified version of the below code obtained from ChatGPT 4o.

.. sourcecode:: python

    """
    kanji_time CLI entry point.
    """

    import argparse
    import importlib
    import os
    import sys
    from types import ModuleType
    from typing import Callable

    # --- Safe Report Registry ---

    VALID_REPORTS = {
        "practice_sheet": "reports.practice_sheet.report",
        "kanji_summary": "reports.kanji_summary.report"
    }

    # --- Entry Point Logic ---

    def main():
        parser = argparse.ArgumentParser(
            prog="kanji_time",
            description="Generate kanji reports using selectable output styles."
        )

        parser.add_argument(
            "kanji",
            nargs="+",
            help="One or more kanji glyphs to generate reports for."
        )

        parser.add_argument(
            "--report", "-r",
            choices=VALID_REPORTS.keys(),
            default="kanji_summary",
            help="Select the report to generate."
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

        if args.help_report:
            show_report_help(args.help_report)
            return

        report_module = load_report_module(args.report)
        generate = getattr(report_module, "generate", None)

        if not callable(generate):
            print(f"Error: The selected report '{args.report}' does not define a callable 'generate(kanji_list: str)' function.", file=sys.stderr)
            sys.exit(1)

        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)

        try:
            generate("".join(args.kanji))
        except Exception as e:
            print(f"Error running report: {e}", file=sys.stderr)
            sys.exit(1)


    def load_report_module(report_name: str) -> ModuleType:
        module_path = VALID_REPORTS[report_name]
        try:
            return importlib.import_module(module_path)
        except Exception as e:
            print(f"Failed to import report '{report_name}' ({module_path}): {e}", file=sys.stderr)
            sys.exit(1)


    def show_report_help(report_name: str):
        module_path = VALID_REPORTS[report_name]
        try:
            module = importlib.import_module(module_path)
            help_text = getattr(module, "__doc__", None)
            print(help_text.strip() if help_text else f"No docstring found for report '{report_name}'.")
        except Exception as e:
            print(f"Failed to load report help for '{report_name}': {e}", file=sys.stderr)
            sys.exit(1)


    if __name__ == "__main__":
        main()
