import uuid

import pytest

from albert import Albert
from albert.resources.btdataset import BTDataset


@pytest.fixture
def dataset(client: Albert) -> BTDataset:
    # api-btdataset does not have working list/delete functionality,
    # so we need to fetch an existing dataset to play with
    return client.btdatasets.get_by_id(id="DST1")


def test_update(client: Albert, dataset: BTDataset):
    key = f"key-{uuid.uuid4()}"
    dataset.key = key
    dataset = client.btdatasets.update(dataset=dataset)
    assert dataset.key == key
