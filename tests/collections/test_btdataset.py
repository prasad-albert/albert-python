from albert import Albert
from albert.resources.btdataset import BTDataset


def test_get_by_id(client: Albert, seeded_btdataset: BTDataset):
    fetched_dataset = client.btdatasets.get_by_id(id=seeded_btdataset.id)
    assert fetched_dataset.id == seeded_btdataset.id


def test_list_by_user(client: Albert):
    user = client.users.get_current_user()
    dataset = next(client.btdatasets.list(created_by=user.id), None)
    assert dataset is not None
    assert dataset.created.by == user.id


def test_update(client: Albert, seeded_btdataset: BTDataset):
    marker = "TEST"
    seeded_btdataset.key = marker
    seeded_btdataset.file_name = marker

    updated_dataset = client.btdatasets.update(dataset=seeded_btdataset)
    assert updated_dataset.key == seeded_btdataset.key
    assert updated_dataset.file_name == seeded_btdataset.file_name
