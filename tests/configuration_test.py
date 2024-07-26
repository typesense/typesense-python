import pytest

from src.typesense.configuration import ConfigDict, Configuration


def test_validate_node_fields_with_url() -> None:
    """Test validate_node_fields with a URL string."""
    assert Configuration.validate_node_fields("http://localhost:8108/path")


def test_validate_node_fields_with_valid_dict() -> None:
    """Test validate_node_fields with a valid dictionary."""
    assert Configuration.validate_node_fields(
        {"host": "localhost", "port": 8108, "protocol": "http"}
    )


def test_validate_node_fields_with_invalid_dict() -> None:
    """Test validate_node_fields with an invalid dictionary."""
    assert not Configuration.validate_node_fields(
        {  # type: ignore[arg-type]
            "host": "localhost",
            "port": 8108,
        }
    )


def test_deprecation_warning_timeout_seconds(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test that a deprecation warning is issued for the 'timeout_seconds' field.
    """
    config_dict: ConfigDict = {
        "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "timeout_seconds": 10,
    }
    Configuration.show_deprecation_warnings(config_dict)
    assert (
        ' '.join(
            [
                "Deprecation warning: timeout_seconds is now renamed",
                "to connection_timeout_seconds",
            ]
        )
        in caplog.text
    )


def test_deprecation_warning_master_node(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test that a deprecation warning is issued for the 'master_node' field.
    """
    config_dict: ConfigDict = {
        "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "master_node": "http://localhost:8108",
    }
    Configuration.show_deprecation_warnings(config_dict)
    assert (
        "Deprecation warning: master_node is now consolidated to nodes" in caplog.text
    )


@pytest.mark.filterwarnings("ignore:Deprecation warning")
def test_deprecation_warning_read_replica_nodes(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test that a deprecation warning is issued for the 'read_replica_nodes' field.
    """
    config_dict: ConfigDict = {
        "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "read_replica_nodes": ["http://localhost:8109"],
    }
    Configuration.show_deprecation_warnings(config_dict)
    assert (
        "Deprecation warning: read_replica_nodes is now consolidated to nodes"
        in caplog.text
    )
