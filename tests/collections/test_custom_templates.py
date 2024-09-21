from collections.abc import Generator

from albert.albert import Albert
from albert.resources.custom_templates import CustomTemplate, CustomTemplateData


def _list_asserts(returned_list):
    # found = False
    for i, u in enumerate(returned_list):
        if i == 50:
            break
        assert isinstance(u, CustomTemplate)
        # found = True
        if hasattr(u, "data"):
            for d in u.data:
                assert isinstance(d, CustomTemplateData)
    # assert found
    # TODO: No custom templates loaded to test yet  :(


def test_basics(client: Albert):
    list_response = client.templates.list()
    assert isinstance(list_response, Generator)
    _list_asserts(list_response)
