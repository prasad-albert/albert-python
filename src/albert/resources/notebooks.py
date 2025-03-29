from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from albert.resources.base import BaseAlbertModel, BaseEntityLink, BaseResource
from albert.resources.identifiers import LinkId, NotebookId, ProjectId, SynthesisId, TaskId


class ListBlockStyles(str, Enum):
    ORDERED = "ordered"
    UNORDERED = "unordered"


class BlockType(str, Enum):
    PARAGRAPH = "paragraph"
    LIST = "list"
    HEADER = "header"
    CHECKLIST = "checklist"
    IMAGE = "image"
    ATTACHES = "attaches"
    KETCHER = "ketcher"
    TABLE = "table"


class BaseBlock(BaseAlbertModel):
    id: str | None = Field(default=None)
    version: datetime | None = Field(default=None)


class HeaderContent(BaseAlbertModel):
    level: Literal[1, 2, 3]
    text: str | None


class HeaderBlock(BaseBlock):
    type: Literal[BlockType.HEADER] = Field(default=BlockType.HEADER, alias="blockType")
    content: HeaderContent


class ParagraphContent(BaseAlbertModel):
    text: str | None


class ParagraphBlock(BaseBlock):
    type: Literal[BlockType.PARAGRAPH] = Field(default=BlockType.PARAGRAPH, alias="blockType")
    content: ParagraphContent


class ChecklistItem(BaseAlbertModel):
    checked: bool
    text: str


class ChecklistContent(BaseAlbertModel):
    items: list[ChecklistItem]


class ChecklistBlock(BaseBlock):
    type: Literal[BlockType.CHECKLIST] = Field(default=BlockType.CHECKLIST, alias="blockType")
    content: ChecklistContent


class AttachesContent(BaseAlbertModel):
    title: str
    namespace: str = Field(default="result")
    file_key: str | None = Field(default=None, alias="fileKey", exclude=True, frozen=True)
    format: str | None = Field(default=None, alias="mimeType", exclude=True, frozen=True)
    signed_url: str | None = Field(default=None, alias="signedURL", exclude=True, frozen=True)


class AttachesBlock(BaseBlock):
    type: Literal[BlockType.ATTACHES] = Field(default=BlockType.ATTACHES, alias="blockType")
    content: AttachesContent


class ImageContent(BaseAlbertModel):
    title: str
    namespace: str = Field(default="result")
    stretched: bool = Field(default=False)
    with_background: bool = Field(default=False, alias="withBackground")
    with_border: bool = Field(default=False, alias="withBorder")
    file_key: str | None = Field(default=None, alias="fileKey", exclude=True, frozen=True)
    signed_url: str | None = Field(default=None, alias="signedURL", exclude=True, frozen=True)


class ImageBlock(BaseBlock):
    type: Literal[BlockType.IMAGE] = Field(default=BlockType.IMAGE, alias="blockType")
    content: ImageContent


class KetcherContent(BaseAlbertModel):
    synthesis_id: SynthesisId | None = Field(default=None, alias="synthesisId")
    name: str | None = Field(default=None)
    id: str | None = Field(default=None)
    block_id: str | None = Field(default=None, alias="blockId")
    data: str | None = Field(default=None)
    file_key: str | None = Field(default=None, alias="fileKey", exclude=True, frozen=True)
    s3_key: str | None = Field(default=None, alias="s3Key", exclude=True, frozen=True)
    png: str | None = Field(default=None, exclude=True, frozen=True)
    ketcher_url: str | None = Field(default=None, alias="ketcherUrl", exclude=True, frozen=True)


class KetcherBlock(BaseBlock):
    type: Literal[BlockType.KETCHER] = Field(default=BlockType.KETCHER, alias="blockType")
    content: KetcherContent


class TableContent(BaseAlbertModel):
    content: list[list[str | None]]
    with_headings: bool = Field(default=False, alias="withHeadings")


class TableBlock(BaseBlock):
    type: Literal[BlockType.TABLE] = Field(default=BlockType.TABLE, alias="blockType")
    content: TableContent


class NotebookListItem(BaseModel):
    content: str | None
    items: list["NotebookListItem"] = []


class BulletedListContent(BaseAlbertModel):
    items: list[NotebookListItem]
    style: Literal[ListBlockStyles.UNORDERED] = ListBlockStyles.UNORDERED


class NumberedListContent(BaseAlbertModel):
    items: list[NotebookListItem]
    style: Literal[ListBlockStyles.ORDERED] = ListBlockStyles.ORDERED


_ListContentUnion = NumberedListContent | BulletedListContent
ListContent = Annotated[_ListContentUnion, Field(discriminator="style")]


class ListBlock(BaseBlock):
    type: Literal[BlockType.LIST] = Field(default=BlockType.LIST, alias="blockType")
    content: ListContent


class NotebookLink(BaseAlbertModel):
    id: LinkId | None = Field(default=None)
    child: BaseEntityLink = Field(..., alias="Child")


_NotebookBlockUnion = (
    HeaderBlock
    | ParagraphBlock
    | ChecklistBlock
    | AttachesBlock
    | ImageBlock
    | KetcherBlock
    | TableBlock
    | ListBlock
)
NotebookBlock = Annotated[_NotebookBlockUnion, Field(discriminator="type")]


class Notebook(BaseResource):
    id: NotebookId | None = Field(default=None, alias="albertId")
    name: str = Field(default="Untitled Notebook")
    parent_id: ProjectId | TaskId = Field(..., alias="parentId")
    version: datetime | None = Field(default=None)
    blocks: list[NotebookBlock] = Field(default_factory=list)
    links: list[NotebookLink] | None = Field(default=None)
