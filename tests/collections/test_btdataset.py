from albert import Albert
from albert.resources.btdataset import BTDataset


def test_update(client: Albert, seeded_btdataset: BTDataset):
    marker = "TEST"
    seeded_btdataset.key = marker
    seeded_btdataset.file_name = marker

    updated_dataset = client.btdatasets.update(dataset=seeded_btdataset)
    assert updated_dataset.key == seeded_btdataset.key
    assert updated_dataset.file_name == seeded_btdataset.file_name
