from pydantic import Field

from albert.resources.base import BaseAlbertModel


class UnNumber(BaseAlbertModel):
    id: str = Field(alias="albertId")
    storage_class_name: str = Field(alias="storageClassName")
    shipping_description: str = Field(alias="shippingDescription")
    storage_class_number: str = Field(alias="storageClassNumber")
    un_number: str = Field(alias="unNumber")
    un_classification: str = Field(alias="unClassification")
