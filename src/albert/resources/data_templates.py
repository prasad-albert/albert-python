from albert.resources.base import BaseAlbertModel, BaseResource
from albert.resources.serialization import SerializeAsEntityLink
from albert.resources.units import Unit


class DataColumn(BaseAlbertModel):
    value: str
    hidden: bool = False
    unit: SerializeAsEntityLink[Unit]
    calculation: str = None
    id: str = None
