from collections.abc import Generator

from albert.albert import Albert
from albert.resources.parameter_groups import ParameterGroup


def _list_asserts(returned_list):
    found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, ParameterGroup)
        found = True
    assert found


def test_basics(client: Albert, seeded_parameter_groups: list[ParameterGroup]):
    list_response = client.parameter_groups.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)


def test_advanced_list(client: Albert, seeded_parameter_groups: list[ParameterGroup]):
    list_response = client.parameter_groups.list(names=[seeded_parameter_groups[0].name])
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)
