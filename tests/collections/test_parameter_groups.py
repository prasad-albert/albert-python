from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.resources.parameter_groups import ParameterGroup


def _list_asserts(returned_list):
    # found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, ParameterGroup)
        # found = True
    # assert found
    # TODO: No custom parameter groups loaded to test yet  :(


@pytest.fixture(scope="module")
def client():
    return Albert()


def test_basics(client: Albert):
    list_response = client.parameter_groups.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)
