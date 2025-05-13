from collections.abc import Iterator

from albert.collections.base import BaseCollection, OrderBy
from albert.collections.patch_utils import _split_patch_types_for_params_and_data_cols
from albert.exceptions import AlbertHTTPError
from albert.resources.parameter_groups import (
    ParameterGroup,
    PGPatchPayload,
    PGType,
)
from albert.session import AlbertSession
from albert.utils.logging import logger
from albert.utils.pagination import AlbertPaginator, PaginationMode


class ParameterGroupCollection(BaseCollection):
    """ParameterGroupCollection is a collection class for managing ParameterGroup entities in the Albert platform."""

    _api_version = "v3"
    _updatable_attributes = {"name", "description", "metadata"}
    # To do: Add the rest of the allowed attributes

    def __init__(self, *, session: AlbertSession):
        """A collection for interacting with Albert parameter groups.

        Parameters
        ----------
        session : AlbertSession
            The Albert session to use for making requests.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{ParameterGroupCollection._api_version}/parametergroups"

    def get_by_id(self, *, id: str) -> ParameterGroup:
        """Get a parameter group by its ID.

        Parameters
        ----------
        id : str
            The ID of the parameter group to retrieve.

        Returns
        -------
        ParameterGroup
            The parameter group with the given ID.
        """
        path = f"{self.base_path}/{id}"
        response = self.session.get(path)
        return ParameterGroup(**response.json())

    def get_by_ids(self, *, ids: list[str]) -> ParameterGroup:
        url = f"{self.base_path}/ids"
        batches = [ids[i : i + 100] for i in range(0, len(ids), 100)]
        return [
            ParameterGroup(**item)
            for batch in batches
            for item in self.session.get(url, params={"id": batch}).json()["Items"]
        ]

    def list(
        self,
        *,
        text: str | None = None,
        types: PGType | list[PGType] | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
        limit: int = 25,
        offset: int | None = None,
    ) -> Iterator[ParameterGroup]:
        """Search for Parameter Groups matching the given criteria.

        Parameters
        ----------
        text : str | None, optional
            Text to search for, by default None
        types : PGType | list[PGType] | None, optional
            Filer the returned Parameter Groups by Type, by default None
        order_by : OrderBy, optional
            The order in which to return results, by default OrderBy.DESCENDING

        Yields
        ------
        Iterator[ParameterGroup]
            An iterator of Parameter Groups matching the given criteria.
        """

        def deserialize(items: list[dict]) -> Iterator[ParameterGroup]:
            for item in items:
                id = item["albertId"]
                try:
                    yield self.get_by_id(id=id)
                except AlbertHTTPError as e:
                    logger.warning(f"Error fetching parameter group {id}: {e}")
            # Currently, the API is not returning metadata for the list_by_ids endpoint, so we need to fetch individually until that is fixed
            # return self.get_by_ids(ids=[x["albertId"] for x in items])

        params = {
            "limit": limit,
            "offset": offset,
            "order": order_by.value,
            "text": text,
            "types": [types] if isinstance(types, PGType) else types,
        }

        return AlbertPaginator(
            mode=PaginationMode.OFFSET,
            path=f"{self.base_path}/search",
            session=self.session,
            params=params,
            deserialize=deserialize,
        )

    def delete(self, *, id: str) -> None:
        """Delete a parameter group by its ID.

        Parameters
        ----------
        id : str
            The ID of the parameter group to delete
        """
        path = f"{self.base_path}/{id}"
        self.session.delete(path)

    def create(self, *, parameter_group: ParameterGroup) -> ParameterGroup:
        """Create a new parameter group.

        Parameters
        ----------
        parameter_group : ParameterGroup
            The parameter group to create.

        Returns
        -------
        ParameterGroup
            The created parameter group.
        """

        response = self.session.post(
            self.base_path,
            json=parameter_group.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        return ParameterGroup(**response.json())

    def get_by_name(self, *, name: str) -> ParameterGroup | None:
        """Get a parameter group by its name.

        Parameters
        ----------
        name : str
            The name of the parameter group to retrieve.

        Returns
        -------
        ParameterGroup | None
            The parameter group with the given name, or None if not found.
        """
        matches = self.list(text=name)
        for m in matches:
            if m.name.lower() == name.lower():
                return m
        return None

    def update(self, *, parameter_group: ParameterGroup) -> ParameterGroup:
        """Update a parameter group.

        Parameters
        ----------
        parameter_group : ParameterGroup
            The updated ParameterGroup. The ParameterGroup must have an ID.

        Returns
        -------
        ParameterGroup
            The updated ParameterGroup as returned by the server.
        """

        existing = self.get_by_id(id=parameter_group.id)
        path = f"{self.base_path}/{existing.id}"

        payload = self._generate_patch_payload(existing=existing, updated=parameter_group)
        # need to use a different payload for the special update parameters
        payload = PGPatchPayload(
            data=payload.data,
        )

        # Handle special update parameters
        special_patches, special_enum_patches, new_param_patches = (
            _split_patch_types_for_params_and_data_cols(existing=existing, updated=parameter_group)
        )

        payload.data.extend(special_patches)
        if len(payload.data) > 0:
            print("SPECIAL PATCHES")
            print(payload)
            self.session.patch(
                path, json=payload.model_dump(mode="json", by_alias=True, exclude_none=True)
            )

        # handle adding new parameters
        if len(new_param_patches) > 0:
            print("NEW PARAM PATCHES")
            print(new_param_patches)
            self.session.put(
                f"{self.base_path}/{existing.id}/parameters",
                json={"Parameters": new_param_patches},
            )
        # Handle special enum update parameters
        for sequence, enum_patches in special_enum_patches.items():
            if len(enum_patches) == 0:
                continue
            print("SPECIAL ENUM PATCHES")
            print(enum_patches)
            enum_path = f"{self.base_path}/{existing.id}/parameters/{sequence}/enums"
            self.session.put(enum_path, json=enum_patches)
        return self.get_by_id(id=parameter_group.id)
