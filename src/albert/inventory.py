import requests
from typing import List, Optional, Union, Dict, Any, Generator
from enum import Enum
from albert.entity.tags import Tag, TagCollection
from albert.entity.cas import Cas
from albert.entity.companies import Company, CompanyCollection
from albert.base_collection import BaseCollection, OrderBy
from pydantic import Field, model_validator, PrivateAttr
from albert.base_tagged_entity import BaseTaggedEntity
from albert.base_entity import BaseAlbertModel
from albert.entity.un_numbers import UnNumber


class InventoryCategory(Enum):
    RAW_MATERIALS = "RawMaterials"
    CONSUMABLES = "Consumables"
    EQUIPMENT = "Equipment"
    FORMULAS = "Formulas"


class UnitCategory(Enum):
    MASS = "mass"
    VOLUME = "volume"
    LENGTH = "length"
    PRESSURE = "pressure"
    UNITS = "units"


class InventoryClass(Enum):
    SHARED = "shared"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    PRIVATE = "private"
    PUBLIC = "public"


class CasAmount(BaseAlbertModel):
    """
    CasAmount is a Pydantic model representing an amount of a given CAS.

    Attributes
    ----------
    id : str
        The unique identifier of the CAS amount.
    min : float, optional
        The minimum amount of the CAS in the formulation.
    max : float, optional
        The maximum amount of the CAS in the formulation.
    _cas : Cas
        The CAS object associated with this amount.
    """

    id: str
    min: float = Field(default=None)
    max: float = Field(default=None)

    # Define a private attribute to store the Cas object
    _cas: Cas = PrivateAttr(None)

    def __init__(
        self, cas: Cas = None, min: float = None, max: float = None, **data: Any
    ):
        """
        CasAmount is a Pydantic model representing an amount of a given Cas.

        Attributes
        ----------
        cas : Cas oject
            The Cas Object albert.entity.cas.Cas
        min : float
            The minimum amount of the given cas in the formulation.
        max : float
            The maximum amount of the given cas in the formulation.
        """

        if cas:
            # Initialize with a Cas object
            super().__init__(id=cas.id, min=min, max=max, **data)
            self._cas = cas
        else:
            # Initialize with id, min, and max (for deserialization)
            super().__init__(**data)
            self._cas = None


class InventoryItem(BaseTaggedEntity):
    """
    InventoryItem is a Pydantic model representing an inventory item.

    Attributes
    ----------
    name : str
        The name of the inventory item.
    description : Optional[str]
        The description of the inventory item.
    category : InventoryCategory
        The category of the inventory item.
    project_id : Optional[str]
        Reqired for Formulas
    unit_category : Optional[UnitCategory]
        The unit category of the inventory item.
    tags : Optional[List[Union[Tag,str]]]
        The tags associated with the inventory item.
    cas : Optional[str]
        The CAS number of the inventory item.
    inventory_class : Optional[InventoryClass]
        The class of the inventory item.
    id : Optional[str]
        The Albert ID of the inventory item.
    company : Optional[Company]
        The company associated with the inventory item.
    session : Optional[AlbertSession]
        The session instance for API interactions.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    category: InventoryCategory
    unit_category: UnitCategory = Field(default=None, alias="unitCategory")
    inventory_class: Optional[InventoryClass] = Field(default=None, alias="class")
    id: Optional[str] = Field(None, alias="albertId")
    company: Optional[Company] = Field(default=None, alias="Company")
    tags: Optional[List[Tag]] = Field(default=[], alias="Tags")
    formula_id: Optional[str] = Field(default=None, alias="formulaId")
    project_id: Optional[str] = Field(default=None, alias="parentId")
    # alias: Optional[str] = Field(default=None)
    cas: Optional[List[CasAmount]] = Field(default=None, alias="Cas")
    _task_config: Optional[List[Dict]] = PrivateAttr(
        default=None
    )  # Read only: comes from task generation
    _symbols: Optional[List[Dict]] = PrivateAttr(
        default=None
    )  # read only: comes from attachments
    _un_number: Optional[UnNumber] = PrivateAttr(
        default=None
    )  # Read only: Comes from attachments
    _acls: Optional[List[Dict]] = PrivateAttr(default=None)  # read only
    _metadata: Optional[List[Dict]] = PrivateAttr(default=None)  # read only
    _minimum: Optional[List[Dict[str, Any]]] = PrivateAttr(default=None)  # To do

    def __init__(self, **data: Any):
        """
        Initalize an an inventory item.

        Attributes
        ----------
        name : str
            The name of the inventory item.
        description : Optional[str]
            The description of the inventory item.
        category : InventoryCategory
            The category of the inventory item.
        unit_category : Optional[UnitCategory]
            The unit category of the inventory item.
        tags : Optional[List[Union[Tag,str]]]
            The tags associated with the inventory item.
        cas : Optional[str]
            The CAS number of the inventory item.
        inventory_class : Optional[InventoryClass]
            The class of the inventory item.
        id : Optional[str]
            The Albert ID of the inventory item.
        company : Optional[Company]
            The company associated with the inventory item.
        """

        super().__init__(**data)
        # handle aliases on private attributes
        if "ACL" in data:
            self._acls = data["ACL"]
        if "Metadata" in data:
            self._metadata = data["Metadata"]
        if "unNumber" in data:
            self._un_number = data["unNumber"]
        if "Symbols" in data:
            self._symbols = data["Symbols"]
        if "TaskConfig" in data:
            self._task_config = data["TaskConfig"]
        if "Minimum" in data:
            self._minimum = data["Minimum"]

    @model_validator(mode="before")
    @classmethod
    def set_unit_category(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the unit category based on the inventory category.

        Parameters
        ----------
        values : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with unit category set.
        """
        category = values.get("category")
        unit_category = values.get("unit_category")
        if unit_category is None:
            if category in (
                InventoryCategory.RAW_MATERIALS,
                InventoryCategory.RAW_MATERIALS.value,
                InventoryCategory.FORMULAS,
                InventoryCategory.FORMULAS.value,
            ):
                values["unit_category"] = UnitCategory.MASS.value
            elif category in (
                InventoryCategory.EQUIPMENT,
                InventoryCategory.EQUIPMENT.value,
                InventoryCategory.CONSUMABLES,
                InventoryCategory.CONSUMABLES.value,
            ):
                values["unit_category"] = UnitCategory.UNITS.value
        return values

    @model_validator(mode="before")
    @classmethod
    def convert_company(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert the company field to a Company object if it is a string.

        Parameters
        ----------
        data : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with company converted.
        """
        company = data.get("company", data.get("Company", None))
        if company:
            if isinstance(company, Company):
                data["company"] = company
            elif isinstance(company, str):
                data["company"] = Company(name=company)
            else:
                pass
                # We do not expect this else to be hit because comapanies should only be Tag or str
        return data

    @model_validator(mode="before")
    @classmethod
    def ensure_formula_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure required fields are present for formulas.

        Parameters
        ----------
        data : Dict[str, Any]
            A dictionary of field values.

        Returns
        -------
        Dict[str, Any]
            Updated field values with required fields ensured.

        Raises
        ------
        AttributeError
            If a required project_id is missing for formulas.
        """
        category_raw = data.get("category", None)
        category = (
            category_raw
            if category_raw is None or isinstance(category_raw, str)
            else category_raw.value
        )
        if category == "Formulas":
            this_project = data.get("project_id", None)
            if not this_project:
                # Some on platform formulas somehow don't have a project_id so check if its already on platform
                if not data.get("albertId", None):
                    raise AttributeError(
                        "A project_id must be supplied for all formulas."
                    )
        return data

    def _to_create_api(self):
        """
        Convert the model to a dictionary suitable for API creation requests.

        Returns
        -------
        Dict[str, Any]
            A dictionary representation of the model suitable for API requests.
        """
        dumped_model = self.model_dump(by_alias=True, exclude_none=True)
        if "Company" in dumped_model:
            if "albertId" in dumped_model["Company"]:
                dumped_model["Company"] = {"id": dumped_model["Company"]["albertId"]}
        if "Tags" in dumped_model:
            new_tags = []
            for t in dumped_model["Tags"]:
                if "albertId" in t:
                    new_tags.append({"id": t["albertId"]})
        if len(new_tags) > 0:
            dumped_model["Tags"] = new_tags
        else:
            del dumped_model["Tags"]
        return dumped_model


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

    def __init__(self, session):
        super().__init__(session=session)
        self.base_url = "/api/v3/inventories"

    def inventory_exists(self, inventory_item: InventoryItem) -> bool:
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
        if hit:
            return True
        else:
            return False

    def get_match_or_none(
        self, inventory_item: InventoryItem
    ) -> Union[InventoryItem, None]:
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
        self, inventory_item: InventoryItem, avoid_duplicates: bool = True
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
            tag_collection.create(t) if t.id is None else t
            for t in inventory_item.tags
        ]
        inventory_item.tags = all_tags
        if inventory_item.company and inventory_item.company.id is None:
            company_collection = CompanyCollection(session=self.session)
            inventory_item.company = company_collection.create(
                inventory_item.company
            )
        # Check to see if there is a match on name + Company already
        if avoid_duplicates:
            existing = self.get_match_or_none(inventory_item=inventory_item)
            if isinstance(existing, InventoryItem):
                print("Inventory Item Already Exists")
                return existing

        response = self.session.post(
            self.base_url,
            json=inventory_item._to_create_api()  # This endpoint has some custom payload configurations so I don't use the normal model_dump() method
        )
        return InventoryItem(**response.json())


    def get_by_id(self, inventory_id: str) -> InventoryItem:
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

    def delete(self, inventory_id: str) -> bool:
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
        inventory_id = (
            inventory_id if inventory_id.startswith("INV") else "INV" + inventory_id
        )
        url = f"{self.base_url}/{inventory_id}"
        response = self.session.delete(url)
        return True

    def _list_generator(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        name: Optional[str] = None,
        cas: Optional[List[Cas]] = None,
        company: Optional[List[Company]] = None,
        category: Optional[List[InventoryCategory]] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Generator:
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
            "orderBy": order_by.value,
            # "exactMatch": str(exact_match).lower(),
        }
        if start_key:
            params["startKey"] = start_key
        if name:
            params["text"] = name
        if category:
            params["category"] = [c.value for c in category]
        if cas:
            params["cas"] = [c.number for c in cas]
        if company:
            params["manufacturer"] = [c.name for c in company if isinstance(c, Company)]
        while True:
            response = self.session.get(
                self.base_url + "/search", params=params
            )
            
            raw_inventory = response.json().get("Items", [])
            if (
                not raw_inventory
                or raw_inventory == []
                or len(raw_inventory) < limit
            ):
                break
            for item in raw_inventory:
                # Unfortunetly, list only returns partial objects, so I need to do a GET on each.
                this_aid = (
                    item["albertId"]
                    if item["albertId"].startswith("INV")
                    else "INV" + item["albertId"]
                )
                yield self.get_by_id(this_aid)


    def list(
        self,
        name: Optional[str] = None,
        cas: Optional[List[Cas]] = None,
        category: Optional[List[InventoryCategory]] = None,
        company: Optional[List[Company]] = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> Optional[Generator[InventoryItem, None, None]]:
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

    def _generate_patch_payload(self, existing, updated) -> dict:
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
                        if c.id in old_cas_map.keys():
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
                    for cas_id in old_cas_map.keys():
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

    def update(self, updated_object: BaseAlbertModel) -> BaseAlbertModel:
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
            response = self.session.patch(
                url, json=change_payload)
        updated_inv = self.get_by_id(inventory_id=updated_object.id)
        return updated_inv
