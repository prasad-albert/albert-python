from albert.collections.base import BaseCollection, OrderBy
from albert.resources.batch_data import BatchData, BatchDataType
from albert.resources.identifiers import TaskId
from albert.session import AlbertSession


class BatchDataCollection(BaseCollection):
    """BatchDataCollection is a collection class for managing BatchData entities in the Albert platform."""

    _api_version = "v3"

    def __init__(self, *, session: AlbertSession):
        """
        Initializes the BatchDataCollection with the provided session.

        Parameters
        ----------
        session : AlbertSession
            The Albert session instance.
        """
        super().__init__(session=session)
        self.base_path = f"/api/{BatchDataCollection._api_version}/batchdata"

    def get(
        self,
        *,
        id: TaskId,
        type: BatchDataType = BatchDataType.TASK_ID,
        limit: int = 100,
        start_key: str | None = None,
        order_by: OrderBy = OrderBy.DESCENDING,
    ) -> BatchData:
        """
        Retrieve BatchData by ID.

        Parameters
        ----------
        id : TaskId
            Unique Id of the selected type.
        type : BatchDataType
            Type of Id for which BatchData will be fetched.
        limit : int, optional
            The maximum number of list entities to return.
        start_key : str, optional
            The primary key of the first item that this operation will evaluate.
        order_by : OrderBy, optional
            The order by which to sort the results, by default OrderBy.DESCENDING
        Returns
        ------
        BatchData
            The BatchData object.
        """
        params = {
            "id": id,
            "limit": limit,
            "type": type,
            "startKey": start_key,
            "orderBy": order_by,
        }
        response = self.session.get(self.base_path, params=params)
        return response.json()
        # return BatchData(**response.json())
