"""Pytest configuration file."""

from glob import glob

import pytest

pytest.register_assert_rewrite("utils.object_assertions")

pytest_plugins = [
    fixture_file.replace("/", ".").replace(".py", "")
    for fixture_file in glob("**/tests/fixtures/[!__]*.py", recursive=True)
]
