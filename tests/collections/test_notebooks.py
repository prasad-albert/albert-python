from albert import Albert
from albert.resources.notebooks import Notebook


def test_get_by_id(client: Albert, seeded_notebooks: list[Notebook]):
    nb1, nb2 = seeded_notebooks

    retrieved_nb1 = client.notebooks.get_by_id(id=nb1.id)
    assert retrieved_nb1.id == nb1.id

    retrieved_nb2 = client.notebooks.get_by_id(id=nb2.id)
    assert retrieved_nb2.id == nb2.id
