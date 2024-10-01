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
    list_response = client.parameter_groups.list(
        text=[seeded_parameter_groups[0].name], types=[seeded_parameter_groups[0].type]
    )
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)


def test_returns_existing(caplog, client: Albert, seeded_parameter_groups: list[ParameterGroup]):
    pg = seeded_parameter_groups[0].model_copy(update={"id": None})
    returned_pg = client.parameter_groups.create(parameter_group=pg)
    assert (
        f"Parameter Group {pg.name} already exists. Returning the exiting parameter group."
        in caplog.text
    )
    assert returned_pg.id == seeded_parameter_groups[0].id
    assert returned_pg.name == seeded_parameter_groups[0].name
