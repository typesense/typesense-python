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


def stringify(argument: _Types) -> str:
    if not isinstance(argument, (str, int, bool)):
        raise InvalidParameter(
            f"Value {argument} is not a string, integer, or boolean.",
        )
    if isinstance(argument, (bool, int)):
        return str(argument).lower()
    return argument


def process_param_list(
    parammeter_list: typing.List[typing.Union[str, bool, int]],
) -> str:
    """
    Concatenate a list of parameters into a string.

    Args:
        parammeter_list (typing.List[str | int | bool]): The list of parameters.

    Returns:
        str: The concatenated parameters

    Raises:
        InvalidParameter: If the value is not a string, integer, or boolean.

    Examples:
        >>> process_param_list(["a", "b", "c"])
        "a,b,c"
        >>> process_param_list([1, 2, 3])
        "1,2,3"
        >>> process_param_list([True, False, True])
        "true,false,true"
        >>> process_param_list([True, 1, "c"])
        "true,1,c"
    """
    stringified_list = [
        stringify(parameter_element) for parameter_element in parammeter_list
    ]
    return ",".join(stringified_list)


def stringify_search_params(parameter_dict: ParamSchema) -> StringifiedParamSchema:
    """
    Convert the search parameters to strings.

    Args:
        parameter_dict (ParamSchema): The search parameters.

    Returns:
        StringifiedParamSchema: The search parameters as strings.

    Raises:
        InvalidParameter: If a value is not a string, integer, or boolean.

    Examples:
        >>> stringify_search_params({"a": 1, "b": "c", "d": True})
        {"a": "1", "b": "c", "d": "true"}
        >>> stringify_search_params({"a": [1, 2, 3], "b": ["c", "d", "e"]})
        {"a": "1,2,3", "b": "c,d,e"}
        >>> stringify_search_params({"a": [True, False, True], "b": [1, 2, 3]})
        {"a": "true,false,true", "b": "1,2,3"}
    """
    stringified_params = {}

    for key, param_value in parameter_dict.items():
        if isinstance(param_value, list):
            stringified_params[key] = process_param_list(param_value)
        elif isinstance(param_value, (bool, int, str)):
            stringified_params[key] = stringify(param_value)
        else:
            raise InvalidParameter(
                f"Value {param_value} is not a string, integer, or boolean",
            )

    return stringified_params
