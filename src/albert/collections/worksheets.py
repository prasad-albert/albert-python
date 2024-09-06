from albert.collections.base_collection import BaseCollection
from albert.resources.worksheets import Worksheet


class WorksheetCollection(BaseCollection):
    def __init__(self,*, session):
        super().__init__(session=session)
        self.base_url = "/api/v3/worksheet"

    def get_by_project_id(self, *, project_id):
        params = {"type": "project", "id": "PRO" + project_id}
        response = self.session.get(self.base_url, params=params)

        response_json = response.json()

        # Sheets are themselves collections, and therefore need access to the session
        sheets = response_json.get("Sheets", None)
        if sheets:
            for s in sheets:
                s["session"] = self.session
                s["project_id"] = response_json["projectId"]
        response_json["session"] = self.session

        return Worksheet(**response_json)
