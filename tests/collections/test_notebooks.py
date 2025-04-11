from collections.abc import Iterator

import pytest

from albert import Albert
from albert.resources.notebooks import Notebook, ParagraphBlock, ParagraphContent
from tests.seeding import generate_notebook_seeds


@pytest.fixture(scope="function")
def seeded_notebook(client: Albert, seed_prefix, seeded_projects) -> Iterator[Notebook]:
    notebook = generate_notebook_seeds(seed_prefix=seed_prefix, seeded_projects=seeded_projects)[0]
    seeded = client.notebooks.create(notebook=notebook)
    yield seeded
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
    marker[0] = ParagraphBlock(content=ParagraphContent(text="Converted block."))  # Convert block
    marker = marker[::-1]  # reverse blocks
    marker = marker[3:]  # remove some blocks

    updated_notebook = client.notebooks.update_block_content(notebook=notebook)
    assert updated_notebook.blocks == notebook.blocks


def test_get_block_by_id(client: Albert, seeded_notebooks: list[Notebook]):
    nb = seeded_notebooks[0]
    block = nb.blocks[0]
    retrieved_block = client.notebooks.get_block_by_id(notebook_id=nb.id, block_id=block.id)
    assert retrieved_block.id == block.id
