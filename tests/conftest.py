"""Pytest configuration file."""

from glob import glob
from pathlib import Path

import pytest

pytest.register_assert_rewrite("utils.object_assertions")

pytest_plugins = [
    ".".join(Path(fixture_file).with_suffix("").parts)
    for fixture_file in glob("**/tests/fixtures/[!__]*.py", recursive=True)
]
