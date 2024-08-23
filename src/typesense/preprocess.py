def stringify_search_params(params):
    return {key:stringify(val) for key, val in params.items()}
import sys

def stringify(val):

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

    if isinstance(val, bool) or isinstance(val, int):
        return str(val).lower()
    else:
        return val