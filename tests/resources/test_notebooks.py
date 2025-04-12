import pytest

from albert.resources.notebooks import BlockType, ParagraphContent, PutDatum, PutOperation


def test_put_datum_content_matches_type():
    with pytest.raises(ValueError, match="The content type and block type do not match."):
        PutDatum(
            id="123",
            type=BlockType.KETCHER,
            content=ParagraphContent(text="test"),
            operation=PutOperation.UPDATE,
        )
