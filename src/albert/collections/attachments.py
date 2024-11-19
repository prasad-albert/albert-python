import mimetypes
from pathlib import Path

from albert.collections.base import BaseCollection
from albert.collections.files import FileCollection
from albert.collections.notes import NotesCollection
from albert.resources.attachments import Attachment
from albert.resources.files import FileCategory, FileNamespace
from albert.resources.notes import Note


class AttachmentCollection(BaseCollection):
    _api_version: str = "v3"
    # _updatable_attributes = {Symbols, symbolId, parentId, revisionDate, unNumber, storageClass, hazardStatement, jurisdiction, language, wgk, uploadType, uploadFeature, symbolsCorrected, jurisdictionCode, languageCode, name, description, extensions}

    def __init__(self, *, session):
        super().__init__(session=session)
        self.base_path = f"/api/{AttachmentCollection._api_version}/attachments"

    def _get_file_collection(self):
        return FileCollection(session=self.session)

    def _get_note_collection(self):
        return NotesCollection(session=self.session)

    def attach_file_to_note(
        self,
        *,
        note_id: str,
        file_name: str,
        file_key: str,
        category: FileCategory = FileCategory.OTHER,
    ) -> Attachment:
        attachment = Attachment(
            parent_id=note_id, name=file_name, key=file_key, namespace="result", category=category
        )
        response = self.session.post(
            url=self.base_path,
            json=attachment.model_dump(by_alias=True, mode="json", exclude_unset=True),
        )
        return Attachment(**response.json())

    def delete(self, *, id: str):
        return self.session.delete(f"{self.base_path}/{id}")

    def upload_and_attach_file_as_note(
        self, parent_id: str, file_path: str, note_text: str = ""
    ) -> Note:
        file_path = Path(file_path)
        file_name = file_path.name
        file_type = mimetypes.guess_type(file_path)[0]
        with open(file_path, "rb") as file:
            file_data = file.read()
        self._get_file_collection().sign_and_upload_file(
            data=file_data,
            name=file_name,
            namespace=FileNamespace.RESULT.value,
            content_type=file_type,
        )
        file_info = self._get_file_collection().get_by_name(
            name=file_name, namespace=FileNamespace.RESULT.value
        )
        note = Note(
            parent_id=parent_id,
            text=note_text,
        )
        registered_note = self._get_note_collection().create(note=note)
        self.attach_file_to_note(
            note_id=registered_note.id,
            file_name=file_name,
            file_key=file_info.name,
        )
        return self._get_note_collection().get_by_id(id=registered_note.id)
