import pytest
from pyscholarly import Scholar, fetch_author_data

@pytest.mark.asyncio
async def test_fetch_author_data():
    # Use a known Google Scholar profile
    author_id = "u5VcrGgAAAAJ"
    data = await fetch_author_data(author_id)
    
    # Basic structure tests
    assert isinstance(data, dict)
    assert "name" in data
    assert "citations" in data
    assert "h_index" in data
    assert "publications" in data
    
    # Data type tests
    assert isinstance(data["citations"]["all"], int)
    assert isinstance(data["h_index"]["all"], int)
    assert isinstance(data["publications"], list)
    
    # Content tests
    assert len(data["name"]) > 0
    assert data["citations"]["all"] >= 0
    assert data["h_index"]["all"] >= 0
    
    if len(data["publications"]) > 0:
        pub = data["publications"][0]
        assert "title" in pub
        assert "citations" in pub
        assert "year" in pub
