"""
check_attrs.py

Attribute-based contract decorators for enforcing class invariants on entry or exit of methods.

This module provides:

    - `check_attrs`: a general-purpose decorator for validating one or more
      instance attributes using a predicate
    - `@require_attr`: shorthand for entry-time attribute checks
    - `@ensure_attr`: shorthand for exit-time attribute checks

All validation failures are logged with `logger.error()` in addition to raising `ValueError`, for auditability even if exceptions are caught.
"""

import logging
from functools import wraps
from collections.abc import Callable
from typing import Any

from enum import Enum


logger = logging.getLogger(__name__)


class CheckOn(Enum):
    """Define when to check a condition."""
    Entry = "entry"  # pylint: disable=invalid-name
    Exit = "exit"  # pylint: disable=invalid-name


def check_attrs(
        *attrs: str,
        predicate: Callable[[str, Any], bool],
        mode: CheckOn = CheckOn.Entry
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Enforce that attributes on `self` satisfy a predicate on entry or exit.

    :param attrs: names of attributes to validate on `self`
    :param predicate: a function (name, value) -> bool that enforces the contract
    :param mode: either CheckOn.Entry (before method runs) or CheckOn.Exit (after method runs)
    :return: the decorated method
    """
    if mode not in (CheckOn.Entry, CheckOn.Exit):
        raise ValueError("mode must be 'entry' or 'exit'")

    def decorator(method: Callable[..., Any]) -> Callable[..., Any]:
        """The function that does the actual work of decorating a method."""
        @wraps(method)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            """The function that does the actual work."""
            if mode == CheckOn.Entry:
                for attr in attrs:
                    value = getattr(self, attr)
                    if not predicate(attr, value):
                        msg = (
                            f"{method.__name__}: Entry check failed — "
                            f"{attr}={value} does not satisfy {predicate.__name__}"
                        )
                        logger.error(msg)
                        raise ValueError(msg)
                return method(self, *args, **kwargs)
            if mode == CheckOn.Exit:
                result = method(self, *args, **kwargs)
                for attr in attrs:
                    value = getattr(self, attr)
                    if not predicate(attr, value):
                        msg = (
                            f"{method.__name__}: Exit check failed — "
                            f"{attr}={value} does not satisfy {predicate.__name__}"
                        )
                        logger.error(msg)
                        raise ValueError(msg)
                return result
            return None
        return wrapper
    return decorator


def require_attr(*attrs: str, predicate: Callable[[str, Any], bool]) -> Callable:
    """
    Shortcut for `check_attrs(..., mode=CheckOn.Entry)`

    :param attrs: attributes to validate on entry
    :param predicate: validation function (name, value) -> bool
    :return: the decorated method
    """
    return check_attrs(*attrs, predicate=predicate, mode=CheckOn.Entry)


def ensure_attr(*attrs: str, predicate: Callable[[str, Any], bool]) -> Callable:
    """
    Shortcut for `check_attrs(..., mode=CheckOn.Exit)`

    :param attrs: attributes to validate on exit
    :param predicate: validation function (name, value) -> bool
    :return: the decorated method
    """
    return check_attrs(*attrs, predicate=predicate, mode=CheckOn.Exit)


def within(min_val: int, max_val: int) -> Callable[[str, Any], bool]:
    """
    Construct a predict that checks input against fixed hard range bounds.

    :param min_value: the least allowed input
    :param max_value: the greatest allowed input

    :return: a function that raises a ValueError if its parameter is not in the  min_value to max_value range (inclusive).
    """

    def _predicate(name, value):
        if not min_val <= value <= max_val:
            raise ValueError(f"{name}={value} not in range [{min_val}, {max_val}]")
        return True
    return _predicate
