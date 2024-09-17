import logging
from collections.abc import Generator, Iterator

from albert.albert_session import AlbertSession
from albert.collections.base import BaseCollection, OrderBy
from albert.collections.cas import Cas
from albert.collections.companies import Company, CompanyCollection
from albert.collections.tags import TagCollection
from albert.resources.base import BaseAlbertModel
from albert.resources.inventory import InventoryCategory, InventoryItem


class InventoryCollection(BaseCollection):
    """
    InventoryCollection is a collection class for managing inventory items.

    Parameters
    ----------
    session : Albert
        The Albert session instance.

    Attributes
    ----------
    base_url : str
        The base URL for inventory API requests.

    Methods
    -------
    create(inventory_item: InventoryItem, avoid_duplicates: bool = True) -> InventoryItem
        Creates a new inventory item.
    get_by_id(inventory_id: str) -> Optional[InventoryItem]
        Retrieves an inventory item by its ID.
    update(inventory_id: str, patch_data: dict) -> bool
        Updates an inventory item by its ID.
    delete(inventory_id: str) -> bool
        Deletes an inventory item by its ID.
    list(limit: int, start_key: Optional[str], name: Optional[List[str]], category: Optional[str], order_by: OrderBy, exact_match: bool) -> Optional[List[InventoryItem]]
        Lists inventory items with optional filters.
    """

    def __init__(self, *, session: AlbertSession):
        super().__init__(session=session)
        self.base_url = "/api/v3/inventories"

    def inventory_exists(self, *, inventory_item: InventoryItem) -> bool:
        """
        Check if an inventory item exists.

        Parameters
        ----------
        inventory_item : InventoryItem
            The inventory item to check.

        Returns
        -------
        bool
            True if the inventory item exists, False otherwise.
        """
        hit = self.get_match_or_none(inventory_item)
        return bool(hit)

    def get_match_or_none(self, *, inventory_item: InventoryItem) -> InventoryItem | None:
        """
        Get a matching inventory item or return None if not found.

        Parameters
        ----------
        inventory_item : InventoryItem
            The inventory item to match.

        Returns
        -------
        Union[InventoryItem, None]
            The matching inventory item or None if not found.
        """
        hits = self.list(name=inventory_item.name, company=[inventory_item.company])
        return next(hits, None)

    def create(
        self, *, inventory_item: InventoryItem, avoid_duplicates: bool = True
    ) -> InventoryItem:
        """
        Create a new inventory item.

        Parameters
        ----------
        inventory_item : InventoryItem
            The inventory item to create.
        avoid_duplicates : bool, optional
            Whether to avoid creating duplicate items (default is True).

        Returns
        -------
        InventoryItem
            The created inventory item.
        """
        category = (
            inventory_item.category
            if isinstance(inventory_item.category, str)
            else inventory_item.category.value
        )
        if category == InventoryCategory.FORMULAS.value:
            # This will need to interact with worksheets
            raise NotImplementedError("Registrations of formulas not yet implemented")
        tag_collection = TagCollection(session=self.session)
        all_tags = [
            tag_collection.create(tag=t) if t.id is None else t for t in inventory_item.tags
        ]
        inventory_item.tags = all_tags
        if inventory_item.company and inventory_item.company.id is None:
            company_collection = CompanyCollection(session=self.session)
            inventory_item.company = company_collection.create(company=inventory_item.company)
        # Check to see if there is a match on name + Company already
        if avoid_duplicates:
            existing = self.get_match_or_none(inventory_item=inventory_item)
            if isinstance(existing, InventoryItem):
                logging.warning("Inventory Item Already Exists")
                return existing

        response = self.session.post(
            self.base_url,
            json=inventory_item._to_create_api(),  # This endpoint has some custom payload configurations so I don't use the normal model_dump() method
        )
        return InventoryItem(**response.json())

    def get_by_id(self, *, inventory_id: str) -> InventoryItem:
        """
        Retrieve an inventory item by its ID.

        Parameters
        ----------
        inventory_id : str
            The ID of the inventory item.

        Returns
        -------
        InventoryItem
            The retrieved inventory item.
        """
        if not inventory_id.startswith("INV"):
            inventory_id = "INV" + inventory_id
        url = f"{self.base_url}/{inventory_id}"
        response = self.session.get(url)
        return InventoryItem(**response.json())

    def delete(self, *, inventory_id: str) -> bool:
        """
        Delete an inventory item by its ID.

        Parameters
        ----------
        inventory_id : str
            The ID of the inventory item.

        Returns
        -------
        bool
            True if the item was deleted, False otherwise.
        """
        inventory_id = inventory_id if inventory_id.startswith("INV") else "INV" + inventory_id
        url = f"{self.base_url}/{inventory_id}"
        self.session.delete(url)
        return True

    def _list_generator(
        self,
        *,
        limit: int = 25,
        offset: int | None = None,
        name: str | None = None,
        cas: list[Cas] | None = None,
        company: list[Company] | None = None,
        category: list[InventoryCategory] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator[InventoryItem, None, None]:
        """
        Generator for listing inventory items with optional filters.

        Parameters
        ----------
        limit : int, optional
            The maximum number of items to retrieve per request (default is 50).
        start_key : Optional[str], optional
            The start key for pagination.
        name : Optional[str], optional
            The name filter for the inventory items.
        cas : Optional[List[Cas]], optional
            The CAS filter for the inventory items.
        company : Optional[List[Company]], optional
            The company filter for the inventory items.
        category : Optional[List[InventoryCategory]], optional
            The category filter for the inventory items.
        order_by : OrderBy, optional
            The order in which to retrieve items (default is OrderBy.DESCENDING).

        Yields
        ------
        InventoryItem
            The next inventory item in the generator.
        """
        # Note there are other parameters we could add supprt for

        params = {
            "limit": str(limit),
            # "orderBy": order_by.value,
            # "exactMatch": str(exact_match).lower(),
        }
        if offset:
            params["offset"] = offset
        if name:
            params["text"] = name
        if category:
            params["category"] = [c.value for c in category]
        if cas:
            params["cas"] = [c.number for c in cas]
        if company:
            params["manufacturer"] = [c.name for c in company if isinstance(c, Company)]
        while True:
            response = self.session.get(self.base_url + "/search", params=params)
            raw_inventory = response.json().get("Items", [])
            start_offset = response.json().get("offset")
            params["offset"] = int(start_offset) + int(limit)
            if not raw_inventory or raw_inventory == [] or len(raw_inventory) < limit:
                break
            for item in raw_inventory:
                # Unfortunetly, list only returns partial objects, so I need to do a GET on each.
                this_aid = (
                    item["albertId"]
                    if item["albertId"].startswith("INV")
                    else "INV" + item["albertId"]
                )
                yield self.get_by_id(inventory_id=this_aid)

    def list(
        self,
        *,
        name: str | None = None,
        cas: list[Cas] | None = None,
        category: list[InventoryCategory] | None = None,
        company: list[Company] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Iterator[InventoryItem]:
        """
        List inventory items with optional filters.

        Parameters
        ----------
        name : Optional[str], optional
            The name filter for the inventory items.
        cas : Optional[List[Cas]], optional
            The CAS filter for the inventory items.
        category : Optional[List[InventoryCategory]], optional
            The category filter for the inventory items.
        company : Optional[List[Company]], optional
            The company filter for the inventory items.
        order_by : OrderBy, optional
            The order in which to retrieve items (default is OrderBy.DESCENDING).

        Returns
        -------
        Optional[Genneraroe[InventoryItem]]
            A generator of inventory items that match the filters, or None if no items match.
        """
        # Note there are other parameters we could add supprt for

        # helpers incase the user fails to provide a list for any of these.
        if isinstance(cas, Cas):
            cas = [cas]
        if isinstance(category, InventoryCategory):
            category = [category]
        if isinstance(company, Company):
            company = [company]
        return self._list_generator(
            name=name, cas=cas, category=category, order_by=order_by, company=company
        )

    def _generate_patch_payload(self, *, existing: InventoryItem, updated: InventoryItem) -> dict:
        """
        Generate the PATCH payload for updating an inventory item.

        Parameters
        ----------
        existing : BaseAlbertModel
            The existing state of the inventory item.
        updated : BaseAlbertModel
            The updated state of the inventory item.

        Returns
        -------
        dict
            The payload for the PATCH request.
        """

        _updatable_attributes_individual = {
            "name",
            "description",
            "unit_category",
            "inventory_class",
        }

        _updatable_attributes_special = {"company", "tags", "cas"}
        payload = {"data": []}
        for attribute in _updatable_attributes_individual:
            old_value = getattr(existing, attribute)
            new_value = getattr(updated, attribute)

            # Get the serialization alias name for the attribute, if it exists
            alias = existing.model_fields[attribute].alias or attribute

            if old_value is None and new_value is not None:
                # Add new attribute
                payload["data"].append(
                    {"operation": "add", "attribute": alias, "newValue": new_value}
                )
            elif old_value is not None and new_value != old_value:
                # Update existing attribute
                payload["data"].append(
                    {
                        "operation": "update",
                        "attribute": alias,
                        "oldValue": old_value,
                        "newValue": new_value,
                    }
                )

        for attribute in _updatable_attributes_special:
            old_value = getattr(existing, attribute)
            new_value = getattr(updated, attribute)
            # # Get the serialization alias name for the attribute, if it exists
            if old_value is None and new_value is not None:
                if attribute == "company":
                    payload["data"].append(
                        {
                            "operation": "add",
                            "attribute": "companyId",
                            "newValue": new_value.id,  # This will be a Company Object
                        }
                    )
                elif attribute == "cas":
                    for c in new_value:
                        payload["data"].append(
                            {
                                "operation": "add",
                                "attribute": "casId",
                                "newValue": c.id,  # This will be a CasAmount Object,
                                "entityId": c.id,
                                "max": c.max,
                                "min": c.min,
                            }
                        )
                elif attribute == "tags":
                    for t in new_value:
                        payload["data"].append(
                            {
                                "operation": "add",
                                "attribute": "tagId",
                                "newValue": t.id,  # This will be a CasAmount Object,
                                "entityId": t.id,
                            }
                        )
            elif old_value is not None and new_value != old_value:
                if attribute == "company":
                    # Update existing attribute
                    payload["data"].append(
                        {
                            "operation": "update",
                            "attribute": "companyId",
                            "oldValue": old_value.id,
                            "newValue": new_value.id,
                        }
                    )
                elif attribute == "cas":
                    old_cas_map = {x.id: x for x in old_value}
                    for c in new_value:
                        if c.id in old_cas_map:
                            this_old_cas = old_cas_map[c.id]
                            if this_old_cas.max == c.max and this_old_cas.min == c.min:
                                continue
                            if this_old_cas.max != c.max:
                                payload["data"].append(
                                    {
                                        "operation": "update",
                                        "attribute": "max",
                                        "entityId": c.id,
                                        "oldValue": this_old_cas.max,
                                        "newValue": c.max,
                                    }
                                )
                            if this_old_cas.min != c.min:
                                payload["data"].append(
                                    {
                                        "operation": "update",
                                        "attribute": "min",
                                        "entityId": c.id,
                                        "oldValue": this_old_cas.min,
                                        "newValue": c.min,
                                    }
                                )
                        else:
                            payload["data"].append(
                                {
                                    "operation": "add",
                                    "attribute": "casId",
                                    "newValue": c.id,  # This will be a CasAmount Object,
                                    "max": c.max,
                                    "min": c.min,
                                }
                            )
                            # Check amounts of related CAS
                    for cas_id in old_cas_map:
                        if cas_id not in [x.id for x in new_value]:
                            payload["data"].append(
                                {
                                    "operation": "delete",
                                    "attribute": "casId",
                                    "entityId": c.id,
                                }
                            )
                elif attribute == "tags":
                    old_tag_map = {x.id: x for x in old_value}
                    old_keys = old_tag_map.keys()
                    new_keys = [x.id for x in new_value]
                    for c in new_value:
                        if c.id in old_keys:
                            continue
                        else:
                            payload["data"].append(
                                {
                                    "operation": "add",
                                    "attribute": "tagId",
                                    # "newValue": c.id, #This will be a Tag Object,
                                    "newValue": c.id,
                                }
                            )
                            # Check amounts of related CAS
                    for tag_id in old_keys:
                        if tag_id not in new_keys:
                            payload["data"].append(
                                {
                                    "operation": "delete",
                                    "attribute": "tagId",
                                    "oldValue": tag_id,
                                }
                            )
        return payload

    def update(self, *, updated_object: BaseAlbertModel) -> BaseAlbertModel:
        """
        Update an inventory item.

        Parameters
        ----------
        updated_object : BaseAlbertModel
            The updated inventory item object.

        Returns
        -------
        BaseAlbertModel
            The updated inventory item retrieved from the server.
        """
        # Fetch the current object state from the server or database
        current_object = self.get_by_id(inventory_id=updated_object.id)

        # Generate the PATCH payload
        patch_payload = self._generate_patch_payload(
            existing=current_object, updated=updated_object
        )

        # Complex patching is not working, so I'm going to do this in a loop :(
        # https://teams.microsoft.com/l/message/19:de4a48c366664ce1bafcdbea02298810@thread.tacv2/1724856117312?tenantId=98aab90e-764b-48f1-afaa-02e3c7300653&groupId=35a36a3d-fc25-4899-a1dd-ad9c7d77b5b3&parentMessageId=1724856117312&teamName=Product%20%2B%20Engineering&channelName=General%20-%20API&createdTime=1724856117312
        url = f"{self.base_url}/{updated_object.id}"
        for change in patch_payload["data"]:
            change_payload = {"data": [change]}
            self.session.patch(url, json=change_payload)
        updated_inv = self.get_by_id(inventory_id=updated_object.id)
        return updated_inv
