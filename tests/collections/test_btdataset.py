import pytest

from albert import Albert
from albert.resources.btdataset import BTDataset
from tests.seeding import PRELOAD_BTDATASET_ID


@pytest.fixture
def dataset(client: Albert) -> BTDataset:
    # api-btdataset does not have working list/delete functionality,
    # so we need to hard-code an existing resource to play with
    return client.btdatasets.get_by_id(id=PRELOAD_BTDATASET_ID)


def test_update(client: Albert, dataset: BTDataset):
    marker = "TEST"
    dataset.key = marker
    dataset.file_name = marker

    updated_dataset = client.btdatasets.update(dataset=dataset)
    assert updated_dataset.key == dataset.key
    assert updated_dataset.file_name == dataset.file_name
