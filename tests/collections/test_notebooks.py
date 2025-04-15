from collections.abc import Iterator

import pytest

from albert import Albert
from albert.exceptions import AlbertException
from albert.resources.notebooks import (
    HeaderBlock,
    HeaderContent,
    Notebook,
    ParagraphBlock,
    ParagraphContent,
)
from tests.seeding import generate_notebook_block_seeds, generate_notebook_seeds


@pytest.fixture(scope="function")
def seeded_notebook(client: Albert, seed_prefix, seeded_projects) -> Iterator[Notebook]:
    notebook = generate_notebook_seeds(seed_prefix=seed_prefix, seeded_projects=seeded_projects)[0]
    seeded = client.notebooks.create(notebook=notebook)
    seeded.blocks = generate_notebook_block_seeds()
    yield client.notebooks.update_block_content(notebook=seeded)
    client.notebooks.delete(id=seeded.id)


def test_get_by_id(client: Albert, seeded_notebooks: list[Notebook]):
    nb = seeded_notebooks[0]
    retrieved_nb = client.notebooks.get_by_id(id=nb.id)
    assert retrieved_nb.id == nb.id


def test_update(client: Albert, seeded_notebook: Notebook):
    notebook = seeded_notebook.model_copy()

    marker = "TEST"
    notebook.name = marker

    updated_notebook = client.notebooks.update(notebook=notebook)
    assert updated_notebook.name == notebook.name


def test_update_block_content(client: Albert, seeded_notebook: Notebook):
    notebook = seeded_notebook.model_copy()
    marker = list(notebook.blocks)
    marker[0] = ParagraphBlock(content=ParagraphContent(text="Converted block."))  # Replace block
    marker = marker[::-1]  # reverse blocks
    marker = marker[3:]  # remove some blocks
    notebook.blocks = marker

    updated_notebook = client.notebooks.update_block_content(notebook=notebook)
    for updated, existing in zip(updated_notebook.blocks, notebook.blocks, strict=True):
        assert updated.id == existing.id
        assert updated.content == existing.content

    # Ensure we can enter blocks with None Fields
    notebook = seeded_notebook.model_copy()
    header_block = HeaderBlock(content=HeaderContent(level=1, text=None))
    notebook.blocks.append(header_block)
    updated_notebook = client.notebooks.update_block_content(notebook=notebook)
    assert updated_notebook.blocks[-1].content.text is None

    # Try to change the type of a notebook block
    notebook = seeded_notebook.model_copy()
    header_block = HeaderBlock(content=HeaderContent(level=1, text="Header block"))
    notebook.blocks.append(header_block)
    notebook = client.notebooks.update_block_content(notebook=notebook)
    paragraph_content = ParagraphContent(text="HeaderBlock to ParagraphBlock")
    notebook.blocks[-1] = ParagraphBlock(id=header_block.id, content=paragraph_content)
    with pytest.raises(AlbertException, match="Cannot convert an existing block type"):
        client.notebooks.update_block_content(notebook=notebook)

    # Try to create notebook blocks with duplicate ids
    notebook = seeded_notebook.model_copy()
    header_block1 = HeaderBlock(content=HeaderContent(level=1, text="Header block 1"))
    header_block2 = HeaderBlock(
        id=header_block1.id, content=HeaderContent(level=1, text="Header block 2")
    )
    notebook.blocks.extend([header_block1, header_block2])
    with pytest.raises(AlbertException, match="You have Notebook blocks with duplicate ids"):
        client.notebooks.update_block_content(notebook=notebook)


def test_get_block_by_id(client: Albert, seeded_notebooks: list[Notebook]):
    nb = seeded_notebooks[0]
    block = nb.blocks[0]
    retrieved_block = client.notebooks.get_block_by_id(notebook_id=nb.id, block_id=block.id)
    assert retrieved_block.id == block.id


def test_create_validation(client: Albert, seeded_projects):
    notebook = Notebook(
        parent_id=seeded_projects[0].id,
        blocks=[ParagraphBlock(content=ParagraphContent(text="test"))],
    )
    with pytest.raises(AlbertException, match="Cannot create a Notebook with pre-filled blocks."):
        client.notebooks.create(notebook=notebook)
