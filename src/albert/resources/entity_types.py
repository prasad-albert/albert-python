from enum import Enum

from pydantic import Field

from albert.resources.base import BaseAlbertModel, BaseResource, EntityLink
from albert.resources.identifiers import CustomFieldId, EntityTypeId


class EntityTypeLink(EntityLink):
    """A specialized EntityLink for entity types that serializes id to albertId.

    This class is used when EntityLinks need to be serialized with 'albertId' instead of 'id'
    in the entity types module.

    Examples
    --------
    >>> link = EntityTypeLink(id="123", name="Test Entity")
    >>> link.model_dump(by_alias=True)
    {'albertId': '123', 'name': 'Test Entity'}
    """

    class Config:
        populate_by_name = True

    id: str = Field(alias="albertId")


class CustomCategory(str, Enum):
    """Categories for custom entity types in Albert.

    These categories determines the base entity type that the entity type is based on.
    """

    PROPERTY = "Property"
    BATCH = "Batch"
    GENERAL = "General"


class EntityTypeService(str, Enum):
    """Services that can be associated with entity types.

    Currently only tasks are supported, but this may be expanded in the future.
    """

    TASKS = "tasks"


class EntityTypeType(str, Enum):
    """Types of entity types in the system.

    Entity types can be either custom (user-defined) or system (built-in).
    """

    CUSTOM = "custom"
    SYSTEM = "system"


class EntitySection(str, Enum):
    """Sections where custom fields can be displayed in the UI.

    Custom fields can be displayed either at the top or bottom of the entity form.
    """

    TOP = "top"
    BOTTOM = "bottom"


class EntityCustomField(BaseAlbertModel):
    """A custom field that can be added to an entity type.

    Custom fields allow users to extend the default entity type with additional data fields.

    Attributes
    ----------
    id : str
        The unique identifier for the custom field.
    section : EntitySection
        Where the field should be displayed in the UI (top or bottom).
    hidden : bool
        Whether the field should be hidden from view. This overrides the standard field visibility.
    default : str | float | None | dict, optional
        The default value for the field, if any. This overrides the standard field default value.
    """

    id: CustomFieldId
    section: EntitySection
    hidden: bool
    default: str | float | None | dict = Field(default=None)


class StandardFieldVisibility(BaseAlbertModel):
    """Controls the visibility of standard fields in the entity type.

    This class determines which standard fields (notes, tags, due date) are visible
    for this entity type.

    Attributes
    ----------
    notes : bool | None
        Whether the notes field is visible.
    tags : bool | None
        Whether the tags field is visible.
    due_date : bool | None
        Whether the due date field is visible.
    """

    notes: bool | None = Field(default=None, alias="Notes")
    tags: bool | None = Field(default=None, alias="Tags")
    due_date: bool | None = Field(default=None, alias="DueDate")


class SearchQueryString(BaseAlbertModel):
    """Search query parameters for entity type filtering.

    These parameters are used to filter entity types in search operations. The parameters
    support template variables that are replaced with actual values during the search.
    Note that to use a variable in the query, it must be a single-select custom field in the top section of the entity type.

    Attributes
    ----------
    DAT : str | None
        Data Template filter parameter. Supports template variables for dynamic filtering.
    PRG : str | None
        Parameter Group filter parameter. Supports template variables for dynamic filtering.

    Examples
    --------
    >>> search_query = SearchQueryString(
    ...     DAT="customField1={customField1}&customField2={customField2}",
    ...     PRG="customField1={customField1}&customField2={customField2}"
    ... )
    >>> # The template variables {customField1} and {customField2} will be replaced
    >>> # with actual values from set custom fields `customField1` and `customField2` respectively during the search operation
    """

    DAT: str | None = Field(default=None)
    PRG: str | None = Field(default=None)


class EntityType(BaseResource):
    """The main entity type model that defines the structure and behavior of entities in Albert.

    Entity types are templates that define what fields are available, how they behave,
    and how they are displayed in the system.

    Attributes
    ----------
    category : CustomCategory
        The category of the entity type (Property, Batch, or General).
    label : str
        The display name of the entity type.
    service : EntityTypeService
        The service this entity type is associated with (currently only tasks).
    type : EntityTypeType
        Whether this is a custom or system entity type.
    prefix : str
        The prefix used for entity IDs of this type.
    custom_fields : list[EntityCustomField] | None
        Custom fields defined for this entity type.
    standard_field_visibility : StandardFieldVisibility | None
        Controls which standard fields are visible.
    search_query_string : SearchQueryString | None
        Search parameters for filtering related Data Templates and Parameter Groups.
    """

    id: EntityTypeId | None = Field(default=None, alias="albertId")
    category: CustomCategory
    label: str
    service: EntityTypeService
    type: EntityTypeType | None = Field(default=EntityTypeType.CUSTOM)
    prefix: str
    custom_fields: list[EntityCustomField] = Field(default=None, alias="customFields")
    standard_field_visibility: StandardFieldVisibility | None = Field(
        default=None, alias="standardFieldVisibility"
    )
    search_query_string: SearchQueryString | None = Field(default=None, alias="searchQueryString")


class OptionType(str, Enum):
    """Types of options that can be used in rule actions.

    Options can be either simple strings or lists of values.
    """

    STRING = "string"
    LIST = "list"


class RuleOption(BaseAlbertModel):
    """Options that can be applied in rule actions.

    These options define what values are available or allowed in a rule action.
    RuleOptions can be used to define cascading options for a field.

    Attributes
    ----------
    type : OptionType | None
        The type of option (string or list).
    values : list[str | EntityTypeLink] | None
        The possible values for this option. Can use a normal EntityLink and it will be converted automatically to an EntityTypeLink.
    """

    class Config:
        use_enum_values = True

    type: OptionType | None = Field(default=None)
    values: list[str | EntityTypeLink] | None = Field(default=None)

    # on init, if the value is an EntityLink, convert it to an EntityTypeLink
    def __init__(self, **data):
        if data.get("values") is not None:
            data["values"] = [
                EntityTypeLink(id=x.id, name=x.name) if isinstance(x, EntityLink) else x
                for x in data["values"]
            ]
        super().__init__(**data)


class RuleAction(BaseAlbertModel):
    """An action that can be taken when a rule is triggered.

    Actions define what happens to a field when certain conditions are met.

    Attributes
    ----------
    target_field : str
        The field that this action affects.
    hidden : bool | None
        Whether the field should be hidden.
    required : bool | None
        Whether the field should be required.
    default : str | EntityLink | float | None
        The default value for the field.
    options : RuleOption | None
        Available options for the field.
    """

    class Config:
        use_enum_values = True

    target_field: str
    hidden: bool | None = Field(default=None)
    required: bool | None = Field(default=None)
    default: str | EntityLink | float | None = Field(default=None)
    options: RuleOption | None = Field(default=None)


class RuleCase(BaseAlbertModel):
    """A case in a rule that defines when actions should be taken.

    Cases define the conditions under which rule actions are triggered.

    Attributes
    ----------
    value : str
        The value that triggers this case.
    actions : list[RuleAction]
        The actions to take when this case is triggered.
    """

    class Config:
        use_enum_values = True

    value: str
    actions: list[RuleAction]


class RuleTrigger(BaseAlbertModel):
    """A trigger that can activate rule cases.

    Triggers define when rule cases should be evaluated.

    Attributes
    ----------
    cases : list[RuleCase]
        The cases that should be evaluated when this trigger is activated.
    """

    class Config:
        use_enum_values = True

    cases: list[RuleCase]


class EntityTypeRule(BaseResource):
    """A rule that defines conditional behavior for entity type fields.

    Rules allow for dynamic behavior of fields based on the values of other fields.

    Attributes
    ----------
    custom_field_id : CustomFieldId
        The ID of the custom field this rule applies to.
    trigger : RuleTrigger
        The triggers that activate this rule.
    """

    class Config:
        use_enum_values = True

    custom_field_id: CustomFieldId = Field(alias="customFieldId")
    trigger: RuleTrigger
