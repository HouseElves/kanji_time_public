# test_cli.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Perform coverage tests for the Kanji time CLI."""

import pytest
import builtins
import types
import sys
import pathlib
from unittest import mock
from kanji_time.kanji_time_cli import (
    cli_entry_point,
    load_report_module,
    show_report_help,
    execute_report,
    VALID_REPORTS
)

@pytest.fixture
def dummy_report_module():
    class DummyData:
        pass

    class DummyReport:
        Data = DummyData
        output_file = "dummy.pdf"

        @staticmethod
        def gather_report_data(glyph):
            return f"data-for-{glyph}"

        def __init__(self, data):
            self._data = data
            self.page_factory = mock.Mock(settings=mock.Mock(page_size=[mock.Mock(pt=595), mock.Mock(pt=842)],
                                                             printable_region="printable"))
            self.state = set(["have_more_data"])
            self.counter = 0

        def begin_page(self, page_number):
            if page_number > 1:
                return False
            return True

        def draw(self, surface, region):
            pass

    module = types.SimpleNamespace(Report=DummyReport, __doc__="Dummy report module.")
    return module

@pytest.mark.parametrize("alias", VALID_REPORTS.keys())
def test_show_report_help_success(alias, dummy_report_module):
    with mock.patch("importlib.import_module", return_value=dummy_report_module):
        show_report_help(alias)

@pytest.mark.parametrize("alias", VALID_REPORTS.keys())
def test_show_report_help_failure(alias):
    with mock.patch("importlib.import_module", side_effect=Exception("Boom")):
        with pytest.raises(ValueError):
            show_report_help(alias)

@pytest.mark.parametrize("alias", VALID_REPORTS.keys())
def test_load_report_module_success(alias, dummy_report_module):
    with mock.patch("importlib.import_module", return_value=dummy_report_module) as importer:
        mod = load_report_module(alias)
        assert mod.Report is dummy_report_module.Report
        assert importer.called

def test_load_report_module_missing_module(monkeypatch):
    monkeypatch.setitem(VALID_REPORTS, "broken", "non.existent.module")
    with pytest.raises(SystemExit):
        load_report_module("broken")

def test_execute_report_missing_parts(dummy_report_module):
    mod = types.SimpleNamespace()
    with pytest.raises(KeyError):
        execute_report("foo", "漢", pathlib.Path("."))

def test_execute_report_success(tmp_path, dummy_report_module):
    """Verify that a defined report runs to completion via a mockup."""
    with (
        mock.patch("kanji_time.kanji_time_cli.load_report_module", return_value=dummy_report_module),
        mock.patch("kanji_time.kanji_time_cli.open_surface") as open_surface,
        mock.patch("kanji_time.kanji_time_cli.init_reportlab")
    ):
        dummy_canvas = mock.MagicMock()
        open_surface.return_value.__enter__.return_value = dummy_canvas
        execute_report("kanji_summary", "漢", tmp_path)
        assert dummy_canvas.showPage.called

def test_cli_help_report(monkeypatch):
    argv = ["kanji_time", "--help-report", "kanji_summary", "--report", "kanji_summary", "漢"]
    monkeypatch.setattr(sys, "argv", argv)
    with mock.patch("kanji_time.kanji_time_cli.show_report_help"):
        cli_entry_point()

def test_cli_missing_output_dir(monkeypatch):
    argv = ["kanji_time", "--report", "kanji_summary", "漢"]
    monkeypatch.setattr(sys, "argv", argv)
    with (
        mock.patch("kanji_time.kanji_time_cli.pathlib.Path.mkdir", side_effect=OSError("fail")),
        pytest.raises(SystemExit) as excinfo
    ):
        cli_entry_point()
    assert excinfo.value.code == 2

def test_cli_full_run(tmp_path, monkeypatch, dummy_report_module):
    argv = ["kanji_time", "--report", "kanji_summary", "台", "所", "-o", str(tmp_path)]
    monkeypatch.setattr(sys, "argv", argv)
    with (
        mock.patch("kanji_time.kanji_time_cli.load_report_module", return_value=dummy_report_module),
        mock.patch("kanji_time.kanji_time_cli.open_surface") as open_surface,
        mock.patch("kanji_time.kanji_time_cli.init_reportlab"),
        mock.patch("kanji_time.kanji_time_cli.log")
    ):
        dummy_canvas = mock.MagicMock()
        open_surface.return_value.__enter__.return_value = dummy_canvas
        cli_entry_point()
        assert dummy_canvas.showPage.called

def test_cli_missing_report_list(monkeypatch):
    argv = ["kanji_time", "-o", ".", "漢"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        cli_entry_point()

def test_cli_bogus_report(monkeypatch):
    argv = ["kanji_time", "-o", ".", "-r", "bogus", "漢"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        cli_entry_point()
