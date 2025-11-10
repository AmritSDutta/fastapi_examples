import pytest
from pydantic import ValidationError
from app.schema.document_record import SearchRequest, DocumentRecord  # adjust import path


# SearchRequest tests
def test_search_request_valid():
    req = SearchRequest(search_term="aromatic fruity wine", limit=3)
    assert req.search_term == "aromatic fruity wine"
    assert req.limit == 3


def test_search_request_default_limit():
    req = SearchRequest(search_term="apple notes")
    assert req.limit == 3  # default value


def test_search_request_invalid_length():
    too_long = "a" * 101
    with pytest.raises(ValidationError) as exc:
        SearchRequest(search_term=too_long, limit=3)
    assert "String should have at most 100 characters" in str(exc.value)


def test_search_request_invalid_limit():
    with pytest.raises(ValidationError) as exc:
        SearchRequest(search_term="fine", limit=10)
    assert "Input should be less than or equal to 5" in str(exc.value)


# DocumentRecord tests
def test_document_record_valid():
    doc = DocumentRecord(name="Lovely Wine", description="Fruity and aromatic")
    assert doc.name == "Lovely Wine"
    assert doc.description == "Fruity and aromatic"


def test_document_record_extra_field_forbidden():
    with pytest.raises(ValidationError) as exc:
        DocumentRecord(name="Test", description="Desc", extra_field="oops")
    assert "Extra inputs are not permitted" in str(exc.value)
