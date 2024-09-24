from collections.abc import Generator

from albert.albert import Albert
from albert.resources.parameters import Parameter


def _list_asserts(returned_list):
    found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, Parameter)
        found = True
    assert found


def test_basics(client: Albert, seeded_parameters: list[Parameter]):
    list_response = client.parameters.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)


def test_advanced_list(client: Albert, seeded_parameters: list[Parameter]):
    list_response = client.parameters.list(names=[seeded_parameters[0].name])
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)


# def test_update(client: Albert, seeded_parameters: list[Parameter]):
#     p = seeded_parameters[0]
#     p.name = "Updated"
#     updated = client.parameters.update(updated_parameter=p)
#     assert updated.name == "Updated"
