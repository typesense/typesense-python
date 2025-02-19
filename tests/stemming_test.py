"""Tests for stemming."""

from typesense.stemming import Stemming


def test_actual_upsert(
    actual_stemming: Stemming,
) -> None:
    """Test that it can upsert a stemming dictionary to Typesense Server."""
    response = actual_stemming.dictionaries.upsert(
        "set_1",
        [{"word": "running", "root": "run"}, {"word": "fishing", "root": "fish"}],
    )

    assert response == [
        {"word": "running", "root": "run"},
        {"word": "fishing", "root": "fish"},
    ]


def test_actual_retrieve_many(
    actual_stemming: Stemming,
) -> None:
    """Test that it can retrieve all stemming dictionaries from Typesense Server."""
    response = actual_stemming.dictionaries.retrieve()
    assert response == {"dictionaries": ["set_1"]}


def test_actual_retrieve(
    actual_stemming: Stemming,
) -> None:
    """Test that it can retrieve a single stemming dictionary from Typesense Server."""
    response = actual_stemming.dictionaries["set_1"].retrieve()
    assert response == {
        "id": "set_1",
        "words": [
            {"word": "running", "root": "run"},
            {"word": "fishing", "root": "fish"},
        ],
    }
