# Kanji Time: Command Line Usage


From the shell, the Kanji Time CLI allows you, the user, to generate one or more Kanji Time report PDFs by giving their aliases and passing one or more kanji glyph parameters for each report.

```bash

    python3 -m kanji_time 鳥 馬 魔 --report=practice_sheet
    python3 -m kanji_time 鳥 --report=kanji_summary

```

# Command-Line Options

The CLI options for Kanji Time are as follows.

```text

    --report=REPORT, -r REPORT
        Run the specified report. Can be used multiple times.

    --output-dir=DIR, -o DIR
        Directory where output PDF files will be saved. Defaults to the current directory.

    --help-report=REPORT
        Show help text for a specific report, including its glyph-specific behavior.

    kanji
        One or more kanji glyphs to generate output for.

```

# Available Reports


These are the currently registered report aliases and their backing modules:

|Report Alias   |Description                                                              |Module                        |
|---------------|-------------------------------------------------------------------------|------------------------------|
|kanji_summary  |kanji image, radical image, readings, and dictionary glosses for a kanji |reports.kanji_summary.report  |
|practice_sheet |stroke diagram and empty practice grids for a kanji                      |reports.practice_sheet.report |

# Exit Codes

Kanji Time sends an exit code back to its host shell when it finishes generating the requested reports.

| Code  | Meaning                                     |
|-------|---------------------------------------------|  
| 0     | Success                                     |
| 1     | Failure during help or report module load   |
| 2     | Failure generating output                   |
