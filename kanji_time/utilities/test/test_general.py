# test_general.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Comprehensive test suite for general.py covering lines that are not covered elsewhere.
"""

import pytest
from importlib import reload
from unittest.mock import patch, mock_open, MagicMock
from kanji_time.external_data.radicals import radical_map, meaning_map, Radical
import kanji_time.utilities.general as ug
from reportlab.lib.pagesizes import letter
import os

# TEST ug.rl_config.allowTableBoundsErrors

def test_rl_config_allow_table_bounds_errors():
    """Ensure table bounds errors are allowed in ReportLab config."""
    assert ug.rl_config.allowTableBoundsErrors is True

# TEST LOGGING CONTEXT MANAGER
def test_log_context():
    """Test the ug.log context manager initializes and logs correctly."""
    with patch("logging.basicConfig") as mock_config, \
         patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        reload(ug)
        with ug.log("test.ug.log", "INFO") as logger_instance:
            logger_instance.info("Test ug.log entry")
        mock_config.assert_called_once()
        mock_logger.info.assert_any_call("Logging started")
        mock_logger.info.assert_any_call("Logging finished")
    reload(ug)

# TEST LOGGING EXCEPTION HANDLING
def test_log_exception_handling():
    """Ensure exceptions inside ug.log context are handled and logged."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        reload(ug)
        with ug.log("test.ug.log", "INFO"):
            raise ValueError("Test exception")
        mock_logger.error.assert_called_once()
    reload(ug)

# TEST ug.flatten FUNCTION
def test_flatten_nested_list():
    """Test flattening a deeply nested list."""
    nested_list = [1, [2, [3, [4, [5]]]]]
    flat_list = ug.flatten(nested_list)
    assert flat_list == [1, 2, 3, 4, 5]

# TEST PDF CANVAS CONTEXT MANAGER
def test_pdf_canvas():
    """Test generating a PDF canvas and saving it."""
    output_file = "test_output.pdf"
    with ug.pdf_canvas(output_file, pagesize=letter) as c:
        c.drawString(100, 750, "Test PDF")
    assert os.path.exists(output_file)
    os.remove(output_file)

# TEST ug.no_dict_mutators IMMUTABILITY
def test_no_dict_mutators():
    """Test making a dictionary immutable using ug.no_dict_mutators."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict["new_key"] = "new_value"
    with pytest.raises(TypeError):
        del immutable_dict["key"]

# TEST DICT MUTATOR BLOCKING METHODS
def test_immutable_dict_pop():
    """Test pop operation on immutable dictionary."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict.pop("key")

def test_immutable_dict_popitem():
    """Test popitem operation on immutable dictionary."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict.popitem()

def test_immutable_dict_clear():
    """Test clear operation on immutable dictionary."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict.clear()

def test_immutable_dict_update():
    """Test update operation on immutable dictionary."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict.update({"new_key": "new_value"})

def test_immutable_dict_setdefault():
    """Test setdefault operation on immutable dictionary."""
    immutable_dict = ug.no_dict_mutators({"key": "value"})
    with pytest.raises(TypeError):
        immutable_dict.setdefault("new_key", "new_value")
