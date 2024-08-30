from __future__ import annotations

import sys

if sys.version_info > (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.exceptions import InvalidParameter


def validate_search(params: typing.Mapping[str, str]) -> None:
    for key in params:
        if not isinstance(params[key], str):
            raise InvalidParameter(
                f"'{key}' field expected a string but was given {type(params[key]).__name__}"
            )
