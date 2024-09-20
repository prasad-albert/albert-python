from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.base import OrderBy
from albert.resources.tags import Tag

from ..seeding.tags import seeded_tags


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, u in enumerate(returned_list):
        found = True
        # just check the first 100
        if i == 100:
            break

        assert isinstance(u, Tag)
        assert isinstance(u.tag, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("TAG")
    assert found


def test_simple_tags_list(client: Albert, seeded_tags):
    simple_list = client.tags.list()
    assert isinstance(simple_list, Generator)
    simple_list = list(simple_list)
    _list_asserts(simple_list)


def test_advanced_tags_list(client: Albert, seeded_tags):
    adv_list = client.tags.list(
        name="inventory-tag-1",
        exact_match=True,
        order_by=OrderBy.ASCENDING,
    )
    assert isinstance(adv_list, Generator)
    adv_list = list(adv_list)

    for t in adv_list:
        assert "inventory-tag-1" in t.tag.lower()
    _list_asserts(adv_list)


def test_get_tag_by(client: Albert, seeded_tags):
    tag_test_str = "inventory-tag-2"

    tag = client.tags.get_by_tag(tag=tag_test_str, exact_match=True)

    assert isinstance(tag, Tag)
    assert tag.tag.lower() == tag_test_str.lower()

    by_id = client.tags.get_by_id(tag_id=tag.id)
    assert isinstance(by_id, Tag)
    assert by_id.tag.lower() == tag_test_str.lower()


def test_tag_exists(client: Albert, seeded_tags):
    assert client.tags.tag_exists(tag="company-tag-2")
    assert not client.tags.tag_exists(tag="Nonesense tag no one would ever make!893y58932y58923")


def test_tag_crud(client: Albert):
    new_tag = Tag(tag="SDK test tag!")
    registered_tag = client.tags.create(tag=new_tag)
    assert client.tags.tag_exists(tag=new_tag.tag)
    assert isinstance(registered_tag, Tag)
    assert registered_tag.tag == "SDK test tag!"
    assert registered_tag.id is not None

    updated_tag = client.tags.rename(old_name=registered_tag.tag, new_name="SDK test tag UPDATED!")
    assert isinstance(updated_tag, Tag)
    assert registered_tag.id == updated_tag.id
    assert updated_tag.tag == "SDK test tag UPDATED!"

    deleted = client.tags.delete(tag_id=updated_tag.id)
    assert deleted
    assert not client.tags.tag_exists(tag="SDK test tag UPDATED!")
