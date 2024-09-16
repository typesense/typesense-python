"""Tests for the preprocess module."""

import pytest

from typesense import exceptions
from typesense.preprocess import (
    ParamSchema,
    process_param_list,
    stringify,
    stringify_search_params,
)


def test_stringify_str() -> None:
    """Test that the function can stringify a string."""
    assert stringify("string") == "string"


def test_stringify_bool() -> None:
    """Test that the function can stringify a boolean."""
    assert stringify(True) == "true"


def test_stringify_int() -> None:
    """Test that the function can stringify an integer."""
    assert stringify(42) == "42"


def test_stringify_float() -> None:
    """Test that the function can stringify a float."""
    with pytest.raises(exceptions.InvalidParameter):
        stringify(3.15)


def test_stringify_list() -> None:
    """Test that the function can stringify a list."""
    with pytest.raises(exceptions.InvalidParameter):
        stringify([1, 2, 3])


def test_concat_string_list() -> None:
    """Test that the function can concatenate a list of strings."""
    assert process_param_list(["a", "b", "c"]) == "a,b,c"


def test_concat_bool_list() -> None:
    """Test that the function can concatenate a list of booleans."""
    assert process_param_list([True, False, True]) == "true,false,true"


def test_concat_int_list() -> None:
    """Test that the function can concatenate a list of integers."""
    assert process_param_list([1, 2, 3]) == "1,2,3"


def test_concat_list_list() -> None:
    """Test that the function can concatenate a list of lists."""
    with pytest.raises(exceptions.InvalidParameter):
        process_param_list([[1, 2], [3, 4], [5, 6]])


def test_concat_params() -> None:
    """Test that the function can concatenate a dictionary of parameters."""
    test_params: ParamSchema = {
        "one": "one",
        "two": 2,
        "three": True,
        "four": [1, 2, 3],
        "five": ["one", "two", "three"],
        "six": [True, False],
        "seven": ["one", 2, True],
    }

    processed_params = stringify_search_params(test_params)
    assert processed_params == {
        "one": "one",
        "two": "2",
        "three": "true",
        "four": "1,2,3",
        "five": "one,two,three",
        "six": "true,false",
        "seven": "one,2,true",
    }
