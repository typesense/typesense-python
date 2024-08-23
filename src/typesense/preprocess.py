import sys

from typesense.exceptions import InvalidParameter

if sys.version_info > (3, 11):
    import typing
else:
    import typing_extensions as typing


_ListTypes = typing.List[typing.Union[str, int, bool]]

_Types = typing.Union[int, str, bool]

ParamSchema: typing.TypeAlias = typing.Dict[
    str,
    typing.Union[
        _Types,
        _ListTypes,
    ],
]


StringifiedParamSchema: typing.TypeAlias = typing.Dict[str, str]


def stringify(val: _Types) -> str:
    if not isinstance(val, (str, int, bool)):
        raise InvalidParameter(f"Value {val} is not a string, integer, or boolean.")
    if isinstance(val, bool) or isinstance(val, int):
        return str(val).lower()
    else:
        return val


