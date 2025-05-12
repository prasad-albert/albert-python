from collections.abc import Iterator

import pytest

from albert import Albert
from albert.resources.btdataset import BTDataset
from tests.helpers import suppress_http_errors


@pytest.fixture
def seeded_btdataset(client: Albert) -> Iterator[BTDataset]:
    dataset = BTDataset(name="Test Dataset")
    dataset = client.btdatasets.create(dataset=dataset)
    yield dataset
    with suppress_http_errors():
        client.btdatasets.delete(id=dataset.id)


def test_update(client: Albert, seeded_btdataset: BTDataset):
    marker = "TEST"
    seeded_btdataset.key = marker
    seeded_btdataset.file_name = marker

    updated_dataset = client.btdatasets.update(dataset=seeded_btdataset)
    assert updated_dataset.key == seeded_btdataset.key
    assert updated_dataset.file_name == seeded_btdataset.file_name
