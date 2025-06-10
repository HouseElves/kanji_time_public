"""Try to run both Kanji Time reports and check for output."""
import pathlib
from kanji_time.kanji_time_cli import execute_report


def test_practice_sheet_output():
    """Conform that the practice sheet runs to completion and drops the right pdf files."""
    landing_dir = pathlib.Path(".")
    glyphs = "成現生"
    execute_report("practice_sheet", glyphs, landing_dir)
    for glyph in glyphs:
        pdf_file = landing_dir / pathlib.Path(f"{glyph}_practice.pdf")
        assert(pdf_file.exists())


def test_kanji_summary_output():
    """Conform that the kanji summary runs to completion and drops the right pdf files."""
    landing_dir = pathlib.Path(".")
    glyphs = "成現生"
    radical_nums = ["62", "96", "100"]
    execute_report("kanji_summary", glyphs, landing_dir)
    for radical_num, glyph in zip(radical_nums, glyphs):
        pdf_file = landing_dir / pathlib.Path(f"{radical_num}_{glyph}_summary.pdf")
        assert(pdf_file.exists())

