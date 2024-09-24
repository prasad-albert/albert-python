from albert.resources.base import BaseAlbertModel, BaseEntityLink, EntityLinkConvertible
from albert.resources.serialization import SerializeAsEntityLink


class FakeEntity(BaseAlbertModel, EntityLinkConvertible):
    id: str
    name: str
    data: float


class FakeContainer(BaseAlbertModel):
    entity: SerializeAsEntityLink[FakeEntity] | None
    entity_list: list[SerializeAsEntityLink[FakeEntity]]


def test_serialize_as_entity_link():
    entity = FakeEntity(id="E123", name="test-entity", data=4.0)
    link = entity.to_entity_link()
    assert link.id == entity.id
    assert link.name == entity.name

    container = FakeContainer(entity=entity, entity_list=[entity, link])
    container = FakeContainer(**container.model_dump(mode="json"))

    # FakeEntity values are converted to BaseEntityLink after round-trip serialization
    assert isinstance(container.entity, BaseEntityLink)
    for entity in container.entity_list:
        assert isinstance(entity, BaseEntityLink)

    # Test with optional values
    container = FakeContainer(entity=None, entity_list=[])
    container = FakeContainer(**container.model_dump(mode="json"))
    assert container.entity is None
    assert not container.entity_list
