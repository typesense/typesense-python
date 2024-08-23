"""Utility functions for asserting that objects have the same attribute values."""

from __future__ import annotations

import difflib
import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


TObj = typing.TypeVar("TObj", bound=object)


def obj_to_dict(
    input_obj: typing.Union[TObj, typing.Dict[str, typing.Any]],
) -> typing.Dict[str, typing.Any]:
    """
    Convert an object to a dictionary.

    If the object is already a dictionary, return it as is.

    Args:
        input_obj: The object to convert.

    Returns:
        The object as a dictionary.
    """
    return input_obj if isinstance(input_obj, typing.Dict) else input_obj.__dict__


def assert_match_object(
    actual: typing.Union[TObj, typing.Dict[str, typing.Any]],
    expected: typing.Union[TObj, typing.Dict[str, typing.Any]],
) -> None:
    """
    Assert that two objects have the same attribute values.

    Args:
        actual: The actual object.
        expected: The expected object.

    Raises:
        AssertionError: If the objects do not have the same attribute values.
    """
    actual_attrs = obj_to_dict(actual)

    expected_attrs = obj_to_dict(expected)

    for key, _ in actual_attrs.items():
        assert key in expected_attrs, f"Attribute {key} not found in expected object"

        if actual_attrs[key] != expected_attrs[key]:
            raise_with_diff([{key: expected_attrs[key]}], [{key: actual_attrs[key]}])


def assert_to_contain_keys(
    actual: typing.Dict[str, typing.Any],
    keys: typing.List[str],
) -> None:
    """Assert that the actual dictionary contains the expected keys."""
    for key in keys:
        assert key in actual, f"Key {key} not found in actual dictionary"


def assert_to_contain_object(
    actual: typing.Union[TObj, typing.Dict[str, typing.Any]],
    expected: typing.Union[TObj, typing.Dict[str, typing.Any]],
) -> None:
    """Assert that two objects have the same attribute values."""
    actual_attrs = obj_to_dict(actual)

    expected_attrs = obj_to_dict(expected)

    for key, _ in expected_attrs.items():
        assert key in actual_attrs, f"Attribute {key} not found in expected object"

        if actual_attrs[key] != expected_attrs[key]:
            raise_with_diff([{key: expected_attrs[key]}], [{key: actual_attrs[key]}])


def assert_object_lists_match(
    actual: typing.List[TObj],
    expected: typing.List[typing.Union[TObj, typing.Dict[str, typing.Any]]],
) -> None:
    """Assert that two lists of objects have the same attribute values."""
    actual_dicts = [obj_to_dict(actual_obj) for actual_obj in actual]
    expected_dicts = [obj_to_dict(expected_obj) for expected_obj in expected]

    actual_counter = typing.Counter(
        tuple(sorted(dict_entry.items())) for dict_entry in actual_dicts
    )
    expected_counter = typing.Counter(
        tuple(sorted(dict_entry.items())) for dict_entry in expected_dicts
    )
    if actual_counter != expected_counter:
        raise_with_diff(expected_dicts, actual_dicts)


def raise_with_diff(
    expected_dicts: typing.Sequence[dict[str, typing.Any]],
    actual_dicts: typing.Sequence[dict[str, typing.Any]],
) -> None:
    """
    Raise an AssertionError with a unified diff of the expected and actual values.

    Args:
        expected: The expected value.
        actual: The actual value.
    """
    expected_str = [str(sorted(dict_entry.items())) for dict_entry in expected_dicts]
    actual_str = [str(sorted(dict_entry.items())) for dict_entry in actual_dicts]
    diff = difflib.unified_diff(
        expected_str,
        actual_str,
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )
    diff_output = "\n".join(diff)
    raise AssertionError(f"Lists do not contain the same elements:\n{diff_output}")
