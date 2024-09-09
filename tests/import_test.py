# mypy: disable-error-code="unreachable"
"""Test that the typing_extensions module is imported when Python version < 3.11."""

import importlib
import sys
from collections import namedtuple

import pytest
from pytest_mock import MockFixture

typing_module_names = [
    "alias",
    "analytics_rule",
    "collection",
    "conversations_model",
    "debug",
    "document",
    "key",
    "multi_search",
    "operations",
    "override",
    "stopword",
    "synonym",
]

module_names = [
    "aliases",
    "analytics_rule",
    "analytics_rules",
    "api_call",
    "client",
    "collection",
    "collections",
    "configuration",
    "conversations_models",
    "document",
    "documents",
    "keys",
    "multi_search",
    "overrides",
    "operations",
    "synonyms",
    "preprocess",
    "stopwords",
]

# Create a namedtuple to mock sys.version_info
VersionInfo = namedtuple(
    "VersionInfo",
    ["major", "minor", "micro", "releaselevel", "serial"],
)


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Test is only for Python < 3.11",
)
def test_import_typing(mocker: MockFixture) -> None:
    """Test that the typing module is imported when Python version is 3.11 or higher."""
    mock_version_info = VersionInfo(3, 11, 0, "final", 0)
    mocker.patch.object(sys, "version_info", mock_version_info)

    # Import modules dynamically and assign them to a list
    modules = [importlib.import_module(f"typesense.{name}") for name in module_names]
    typing_modules = [
        importlib.import_module(f"typesense.types.{name}")
        for name in typing_module_names
    ]

    for module in modules:
        assert "typing" in module.__dict__
        assert module.typing == importlib.import_module("typing")

    for module in typing_modules:
        assert "typing" in module.__dict__
        assert module.typing == importlib.import_module("typing")


def test_import_typing_extensions(mocker: MockFixture) -> None:
    """Test that the typing_extensions module is imported when Python version < 3.11."""
    mock_version_info = VersionInfo(3, 10, 0, "final", 0)
    mocker.patch.object(sys, "version_info", mock_version_info)

    # Import modules dynamically and assign them to a list
    init_imports = [
        importlib.import_module(f"typesense.{name}") for name in module_names
    ]
    modules = [importlib.reload(import_module) for import_module in init_imports]

    init_typing_imports = [
        importlib.import_module(f"typesense.types.{name}")
        for name in typing_module_names
    ]

    typing_modules = [
        importlib.reload(import_module) for import_module in init_typing_imports
    ]

    for module in modules:
        assert "typing" in module.__dict__
        assert module.typing == importlib.import_module("typing_extensions")

    for module in typing_modules:
        assert "typing" in module.__dict__
        assert module.typing == importlib.import_module("typing_extensions")
