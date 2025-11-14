"""Logging configuration for the Typesense Python client."""

import functools
import logging
import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

logger = logging.getLogger("typesense")
logger.setLevel(logging.WARN)

_deprecation_warnings: typing.Dict[str, bool] = {}

if sys.version_info >= (3, 11):
    from typing import ParamSpec, TypeVar
else:
    from typing_extensions import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def warn_deprecation(
    message: str,
    *,
    flag_name: typing.Union[str, None] = None,
) -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, R]]:
    """
    Decorator to warn about deprecation when a method is called.

    This decorator will log a deprecation warning once per flag_name when the
    decorated method is called. The warning is only shown once to avoid spam.

    Args:
        message: The deprecation warning message to display.
        flag_name: Optional name for the warning flag. If not provided, a default
            name will be generated based on the function's module and name.

    Returns:
        A decorator function that wraps the target method.

    Example:
        >>> @warn_deprecation("This method is deprecated", flag_name="my_method")
        ... def my_method(self):
        ...     return "result"
    """

    def decorator(func: typing.Callable[P, R]) -> typing.Callable[P, R]:
        if flag_name is None:
            flag = f"{func.__module__}.{func.__qualname__}"
        else:
            flag = flag_name

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            suppress_warnings = False
            if (
                args
                and len(args) > 1
                and args[1]
                and args[1].__class__.__name__ == "ApiCall"
                and hasattr(args[1], "config")
            ):
                suppress_warnings = getattr(
                    args[1].config, "suppress_deprecation_warnings", False
                )

            if not suppress_warnings and not _deprecation_warnings.get(flag, False):
                logger.warning(f"Deprecation warning: {message}")
                _deprecation_warnings[flag] = True
            return func(*args, **kwargs)

        return typing.cast(typing.Callable[P, R], wrapper)

    return decorator
