from albert.entity.tags import Tag, TagCollection
from albert.albert import Albert
from albert.base_collection import OrderBy
import pytest
from typing import Generator


@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    for i, u in enumerate(returned_list):
        # just check the first 100
        if i == 100:
            break
        assert isinstance(u, Tag)
        assert isinstance(u.tag, str)
        assert isinstance(u.id, str)
        assert u.id.startswith("TAG")


def test_simple_tags_list(client):
    simple_list = client.tags.list()
    assert isinstance(simple_list, Generator)
    _list_asserts(simple_list)


def test_advanced_tags_list(client):
    adv_list = client.tags.list(
        name="Lenore",
        exact_match=False,
        order_by=OrderBy.ASCENDING,
    )
    assert isinstance(adv_list, Generator)
    for t in adv_list:
        assert "lenore" in t.tag.lower()
    _list_asserts(adv_list)


def test_get_tag_by(client):
    tag = client.tags.get_by_tag("Lenore's New Tag!", exact_match=False)

    assert isinstance(tag, Tag)
    assert tag.tag.lower() == "lenore's new tag!"

    by_id = client.tags.get_by_id(tag.id)
    assert isinstance(by_id, Tag)
    assert by_id.tag.lower() == "lenore's new tag!"


def test_tag_exists(client):
    assert client.tags.tag_exists("Lenore's New Tag!")
    assert not client.tags.tag_exists(
        "Nonesense tag no one would ever make!893y58932y58923"
    )


def test_tag_crud(client):
    new_tag = Tag(tag="SDK test tag!")
    registered_tag = client.tags.create(new_tag)
    assert isinstance(registered_tag, Tag)
    assert registered_tag.tag == "SDK test tag!"
    assert registered_tag.id is not None

    updated_tag = client.tags.rename(registered_tag.tag, "SDK test tag UPDATED!")
    assert isinstance(updated_tag, Tag)
    assert registered_tag.id == updated_tag.id
    assert updated_tag.tag == "SDK test tag UPDATED!"

    deleted = client.tags.delete(updated_tag.id)
    assert deleted
    assert not client.tags.tag_exists(tag="SDK test tag UPDATED!")
