import json

from albert.collections.base import BaseCollection
from albert.resources.entity_types import EntityType, EntityTypeRule, EntityTypeService
from albert.resources.identifiers import EntityTypeId
from albert.session import AlbertSession
from albert.utils.pagination import AlbertPaginator, PaginationMode


class EntityTypeCollection(BaseCollection):
    """A collection for managing EntityType resources in Albert.

    This collection provides methods for creating, reading, updating, and deleting entity types,
    as well as managing their associated rules. Entity types define the structure and behavior
    of entities in the Albert system.

    Attributes
    ----------
    _api_version : str
        The API version to use for all requests.
    _updatable_attributes : set[str]
        The set of attributes that can be updated on an entity type.
    """

    _api_version = "v3"
    _updatable_attributes = {
        "templateBased",
        "label",
        "lockedTemplate",
        "customFields",
        "standardFieldVisibility",
        "searchQueryString",
    }

    def __init__(self, *, session: AlbertSession):
        """Initialize the EntityTypeCollection with the provided session."""
        super().__init__(session=session)
        self.base_path = f"/api/{EntityTypeCollection._api_version}/entitytypes"

    def create(self, *, entity_type: EntityType) -> EntityType:
        """Creates a new entity type.

        Parameters
        ----------
        entity_type : EntityType
            The entity type to create.

        Returns
        -------
        EntityType
            The created entity type with its ID and other server-generated fields.
        """
        response = self.session.post(
            self.base_path, json=entity_type.model_dump(exclude_none=True, by_alias=True)
        )
        return EntityType(**response.json())

    def delete(self, *, id: EntityTypeId) -> None:
        """Deletes an entity type by its ID.

        Parameters
        ----------
        id : EntityTypeId
            The ID of the entity type to delete.

        Returns
        -------
        None
            The method does not return anything.
        """
        self.session.delete(f"{self.base_path}/{id}")

    def update(self, *, updated_entity_type: EntityType) -> EntityType:
        """Updates an existing entity type.

        This method performs a PATCH operation, only updating the fields that have changed.
        The update is performed by comparing the existing entity type with the updated one
        and generating a patch payload for the changed fields.

        Parameters
        ----------
        updated_entity_type : EntityType
            The entity type with updated fields.

        Returns
        -------
        EntityType
            The updated entity type as returned by the server.
        """
        existing_entity_type = self.get_by_id(id=updated_entity_type.id)
        patches = self._generate_patch_payload(
            existing=existing_entity_type,
            updated=updated_entity_type,
        )
        self.session.patch(f"{self.base_path}/{updated_entity_type.id}", json=patches)
        return self.get_by_id(id=updated_entity_type.id)

    def set_rules(self, *, id: EntityTypeId, rules: list[EntityTypeRule]) -> list[EntityTypeRule]:
        """Sets the rules for an entity type.

        Parameters
        ----------
        id : EntityTypeId
            The ID of the entity type to set rules for.
        rules : list[EntityTypeRule]
            The list of rules to set.

        Returns
        -------
        list[EntityTypeRule]
            The updated list of rules as returned by the server.
        """
        print(
            json.dumps([x.model_dump(exclude_none=True, by_alias=True) for x in rules], indent=2)
        )
        response = self.session.put(
            f"{self.base_path}/rules/{id}",
            json=[x.model_dump(exclude_none=True, by_alias=True) for x in rules],
        )
        return [EntityTypeRule(**x) for x in response.json()]

    def delete_rules(self, id: EntityTypeId) -> None:
        """Deletes all rules for an entity type.

        Parameters
        ----------
        id : EntityTypeId
            The ID of the entity type to delete rules for.

        Returns
        -------
        None
            The method does not return anything.
        """
        self.session.delete(f"{self.base_path}/rules/{id}")

    def get_rules(self, *, id: EntityTypeId) -> list[EntityTypeRule]:
        """Gets all rules for an entity type.

        Parameters
        ----------
        id : EntityTypeId
            The ID of the entity type to get rules for.

        Returns
        -------
        list[EntityTypeRule]
            The list of rules for the entity type.
        """
        response = self.session.get(f"{self.base_path}/rules/{id}")
        return [EntityTypeRule(**x) for x in response.json()]

    def get_by_id(self, *, id: EntityTypeId) -> EntityType:
        """Gets an entity type by its ID.

        Parameters
        ----------
        id : EntityTypeId
            The ID of the entity type to get.

        Returns
        -------
        EntityType
            The entity type with the specified ID.
        """
        response = self.session.get(f"{self.base_path}/{id}")
        return EntityType(**response.json())

    def list(
        self,
        *,
        limit: int = 100,
        start_key: str | None = None,
        order_by: str | None = None,
        service: EntityTypeService | None = None,
    ) -> AlbertPaginator[EntityType]:
        """Lists EntityType entities with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of EntityTypes to return, by default 100.
        start_key : str | None, optional
            The primary key of the first item to evaluate for pagination.
        order_by : str | None, optional
            The field to order the results by.
        service : EntityTypeService | None, optional
            Filter entity types by service (e.g., tasks).

        Returns
        -------
        AlbertPaginator[EntityType]
            A paginator that yields EntityType objects.
        """
        params = {
            "limit": limit,
            "startKey": start_key,
            "orderBy": order_by,
            "service": service.value if service else None,
        }
        return AlbertPaginator(
            mode=PaginationMode.KEY,
            path=self.base_path,
            session=self.session,
            params=params,
            deserialize=lambda items: [EntityType(**item) for item in items],
        )
