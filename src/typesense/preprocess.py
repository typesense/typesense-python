"""
Functionality for preprocessing parameters in the Typesense Python client library.

This module contains utility functions for converting various data types to strings and
processing parameter lists and dictionaries. These functions are used to prepare
data for API requests to Typesense.

Key features:
- Convert individual values (int, str, bool) to strings
- Process lists of parameters into comma-separated strings
- Stringify search parameter dictionaries

Functions:
    stringify: Convert a single value to a string.
    process_param_list: Convert a list of parameters to a comma-separated string.
    stringify_search_params: Convert a dictionary of search parameters to strings.

Types:
    _ListTypes: Type alias for a list of strings, integers, or booleans.
    _Types: Type alias for a single string, integer, or boolean.
    ParamSchema: Type alias for a dictionary of search parameters.
    StringifiedParamSchema: Type alias for a dictionary of stringified search parameters.

Dependencies:
    - typesense.exceptions: Provides InvalidParameter exception
    - typing or typing_extensions: For type hinting

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

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
    """
    Convert a single value to a string.

    Args:
        argument (_Types): The value to be converted to a string.

    Returns:
        str: The stringified version of the input.

    Raises:
        InvalidParameter: If the input is not a string, integer, or boolean.

    Examples:
        >>> stringify(True)
        'true'
        >>> stringify(42)
        '42'
        >>> stringify("Hello")
        'Hello'
    """
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

    This function takes a dictionary of search parameters and converts all values
    to their string representations. List values are converted to comma-separated strings.

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
    stringified_params: StringifiedParamSchema = {}
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
