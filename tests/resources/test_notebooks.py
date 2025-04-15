import pytest

from albert.exceptions import AlbertException
from albert.resources.notebooks import BlockType, ParagraphContent, PutBlockDatum, PutOperation


def test_put_datum_content_matches_type():
    with pytest.raises(AlbertException, match="The content type and block type do not match."):
        PutBlockDatum(
            id="123",
            type=BlockType.KETCHER,
            content=ParagraphContent(text="test"),
            operation=PutOperation.UPDATE,
        )
