from pydantic import BaseModel, ConfigDict


class BaseAlbertModel(BaseModel):
    """Base class for Albert Pydantic models with default configuration settings."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )
