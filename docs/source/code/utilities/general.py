"""General purpose utility items that have no better place to reside."""
# pylint: disable=fixme

from collections.abc import Mapping
from contextlib import contextmanager
from typing import TypeVar

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# pylint: disable=wrong-import-order,wrong-import-position
from reportlab import rl_config
rl_config.allowTableBoundsErrors = True

# pylint: disable=wrong-import-position, wrong-import-order
import logging
logger = logging.getLogger(__name__)


K = TypeVar('K')
V = TypeVar('V')


def coalesce_None(d: Mapping[K, V], key: K, default: V) -> V:  # pylint: disable=invalid-name
    """Produce something similar to SQL's COALESCE function."""
    return value if (value := d.get(key)) is not None else default


@contextmanager
def log(output_filename, level):
    """
    Manage a logger instance.

    :param output_filename: target for the log messages.
    :param level: urgency level for filtering log messages.

    :return: a context manager protecting the open logging channel and file.
    """
    # Code to acquire resource, e.g.:
    logging.basicConfig(filename=output_filename, filemode='w', level=level)
    logger.info('Logging started')
    try:
        yield logger
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Unhandled exception %s", exc_info=e)
        print(f"Unhandled exception:  {e}.")
    finally:
        logger.info('Logging finished')
        print(f"Finished.  Execution log in {output_filename}")


def flatten(nested_list):
    """Flatten a nested list structure iteratively to prevent recursion errors."""
    stack = [nested_list]
    flattened = []

    while stack:
        current = stack.pop()
        if isinstance(current, list):
            stack.extend(reversed(current))  # Reverse to maintain order
        else:
            flattened.append(current)

    return flattened


@contextmanager
def pdf_canvas(output_filename, pagesize=letter):
    """Manage a ReportLab drawing surface for a PDF."""
    # Code to acquire resource, e.g.:
    c = canvas.Canvas(output_filename, pagesize=pagesize)
    try:
        yield c
    finally:
        # Does this only save on failure?  I'm not catching anything so mayyyyybe....
        c.save()
        logging.info("PDF saved to '%s'", output_filename)


def no_dict_mutators(target: dict):
    """
    Convert a vanilla Python dictionary into a pseudo-immutable version.

    The intended use case for this type is for bug traps:
    I want to know if I'm editing a data structure in-place that I shouldn't be editing.

    :param target: a Python dictionary to make (mostly) immutable.
    :return: A subclass of `dict` that raises a TypeError on mutation attempts.
    """

    class _no_dict_mutators(dict):  # pylint: disable=invalid-name
        """Mask the mutator methods of a dict with a TypeError exceptions."""

        def __init__(self, *args, **kwargs):
            """Pass initialization on to the native dictionary."""
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            """Mask the 'dict[index] = ' operation."""
            raise TypeError("Cannot set an element in an immutable mapping")

        def __delitem__(self, key):
            """Mask the 'del dict[index]' operation."""
            raise TypeError("Cannot delete an element in an immutable mapping")

        __marker = object()

        def pop(self, key, default=__marker):
            """Mask the access-and-remove 'dict.pop()' operation."""
            raise TypeError("Cannot pop an immutable mapping")

        def popitem(self):
            """Mask the remove-all 'dict.popitem()' operation."""
            raise TypeError("Cannot popitem on an immutable mapping")

        def clear(self):
            """Mask the remove-all 'dict.clear()' operation."""
            raise TypeError("Cannot clear an immutable mapping")

        def update(self, other=(), /, **kwds):
            """Mask the merge-dictionaries 'dict.update()' operation."""
            raise TypeError("Cannot update an immutable mapping")

        def setdefault(self, key, default=None):
            """Mask the default value setter operation 'dict.setdefault()'."""
            raise TypeError("Cannot setdefault for an immutable mapping")

    return _no_dict_mutators(target)
