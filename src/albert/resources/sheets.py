from copy import copy
from enum import Enum
from typing import Any

import pandas as pd
from pydantic import Field, PrivateAttr, model_validator

from albert.resources.base import BaseAlbertModel, BaseSessionModel
from albert.resources.inventory import InventoryItem


class CellColor(str, Enum):
    WHITE = "RGB(255, 255, 255)"
    RED = "RGB(255, 161, 161)"
    GREEN = "RGB(130, 222, 198)"
    BLUE = "RGB(214, 233, 255)"
    YELLOW = "RGB(254, 240, 159)"
    ORANGE = "RGB(255, 227, 210)"
    PURPLE = "RGB(238, 215, 255)"


class CellType(str, Enum):
    INVENTORY = "INV"
    APP = "APP"
    BLANK = "BLK"
    FORMULA = "Formula"
    TAG = "TAG"
    PRICE = "PRC"
    PDC = "PDC"
    BAT = "BAT"
    TOTAL = "TOT"
    TAS = "TAS"
    DEF = "DEF"
    LKP = "LKP"
    FOR = "FOR"
    EXTINV = "EXTINV"


class DesignType(str, Enum):
    APPS = "apps"
    PRODUCTS = "products"
    RESULTS = "results"


class Cell(BaseAlbertModel):
    column_id: str = Field(alias="colId")
    row_id: str = Field(alias="rowId")
    value: str | dict = ""
    type: CellType
    name: str
    calculation: str = ""
    design_id: str
    format: dict = Field(default={}, alias="cellFormat")

    @property
    def raw_value(self):
        if isinstance(self.value, str):
            return self.value
        else:
            return self.value["value"]

    @property
    def color(self):
        return self.format.get("bgColor", None)


class Component(BaseAlbertModel):
    inventory_item: InventoryItem
    amt_cell: float
    _cell: Cell = None  # read only property set on registrstion

    @property
    def cell(self):
        return self._cell


class DesignState(BaseAlbertModel):
    collapsed: bool | None = False


class Formulations(BaseAlbertModel):
    id: str = Field(alias="formulaId")
    name: str


class Design(BaseSessionModel):
    state: DesignState | None = Field({})
    id: str = Field(alias="albertId")
    design_type: DesignType = Field(alias="designType")
    _grid: pd.DataFrame = PrivateAttr(default=None)
    _rows: list["Row"] = PrivateAttr(default=None)
    _columns: list["Column"] = PrivateAttr(default=None)
    _sheet: "Sheet" = PrivateAttr(default=None)

    def _grid_to_cell_df(self, grid_response):
        all_rows = []
        all_index = []

        for item in grid_response["Items"]:
            row = {}
            this_row_id = item["rowId"]
            row_type = item["type"]
            # row_name = item["name"]
            this_index = item["rowUniqueId"]
            all_index.append(this_index)
            # "rowHeight": "0",# These are also available if I need them
            # "rowHierarchy": [
            #     "apps",
            #     "ROW7"
            # ],
            for c in item["Values"]:
                c["rowId"] = this_row_id
                c["design_id"] = self.id
                c["type"] = row_type
                this_cell = Cell(**c)
                row[f"{c["colId"]}#{c["name"]}"] = this_cell
            all_rows.append(row)
        return pd.DataFrame.from_records(all_rows, index=all_index)

    @property
    def sheet(self):
        return self._sheet

    @property
    def grid(self):
        if self._grid is None:
            self._grid = self._get_grid()
        return self._grid

    def _get_columns(self, grid_response) -> list["Column"]:
        columns = []
        # rsp_json = response.json()
        first_row = grid_response["Items"][0]
        for v in first_row["Values"]:
            columns.append(
                Column(
                    colId=v["colId"],
                    name=v["name"],
                    type=v["type"],
                    session=self.session,
                    sheet=self.sheet,
                )
            )
        return columns

    def _get_rows(self, grid_response) -> list["Column"]:
        rows = []
        rows_dicts = grid_response["Items"]

        for v in rows_dicts:
            rows.append(
                Row(
                    name=v["name"],
                    rowId=v["rowId"],
                    type=v["type"],
                    session=self.session,
                    design=self,
                    sheet=self.sheet,
                    manufacturer=getattr(v, "manufacturer", None),
                    id=getattr(v, "id", None),
                )
            )
        return rows

    def _get_grid(self):
        endpoint = f"/api/v3/worksheet/{self.id}/{self.design_type}/grid"
        response = self.session.get(endpoint)

        resp_json = response.json()
        self._columns = self._get_columns(resp_json)
        self._rows = self._get_rows(resp_json)
        return self._grid_to_cell_df(resp_json)

    @property
    def columns(self) -> list["Column"]:
        if not self._columns:
            self._get_grid()
        return self._columns

    @property
    def rows(self) -> list["Row"]:
        if not self._rows:
            self._get_grid()
        return self._rows


class Sheet(BaseSessionModel):
    id: str = Field(alias="albertId")
    name: str
    formulations: list[Formulations] | None = Field(None)
    hidden: bool
    app_design: Design
    product_design: Design
    result_design: Design
    designs: list[Design] = Field(alias="Designs")
    project_id: str
    _grid: pd.DataFrame = PrivateAttr(default=None)

    @model_validator(mode="before")
    @classmethod
    def set_design_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        category_raw = data.get("Designs")
        if category_raw:
            for c in category_raw:
                c["session"] = data["session"]
                if c["designType"] == "apps":
                    data["app_design"] = c
                elif c["designType"] == "products":
                    data["product_design"] = c
                elif c["designType"] == "results":
                    data["result_design"] = c
        return data

    @model_validator(mode="after")
    def set_sheet_fields(self) -> "Sheet":
        sheet_set_designs = []
        for d in self.designs:
            d._sheet = self
            sheet_set_designs.append(d)
        self.designs = sheet_set_designs
        self.app_design._sheet = self
        self.product_design._sheet = self
        self.result_design._sheet = self
        return self

    @property
    def grid(self):
        if self._grid is None:
            grids = [
                self.product_design,
                self.result_design,
                self.app_design,
            ]  # I don't just use the designs property, so I can ensure order.
            self._grid = pd.concat([x.grid for x in grids])
        return self._grid

    @grid.setter
    def grid(self, value: pd.DataFrame | None):
        self._grid = value
        if value is None:
            for design in self.designs:
                design._grid = None  # Assuming Design has a grid property
        else:
            raise NotImplementedError("grid is a read-only property")

    @property
    def columns(self) -> list["Column"]:
        """The columns of a given sheet"""
        return self.app_design.columns

    @property
    def rows(self) -> list["Row"]:
        """The rows of a given sheet"""
        rows = []
        for d in self.designs:
            rows.extend(d.rows)
        return rows

    def _get_design_id(self, design: DesignType):
        if design == DesignType.APPS:
            return self.app_design.id
        elif design == DesignType.PRODUCTS:
            return self.product_design.id
        elif design == DesignType.RESULTS:
            return self.result_design.id

    def _get_design(self, design: DesignType):
        if design == DesignType.APPS:
            return self.app_design
        elif design == DesignType.PRODUCTS:
            return self.product_design
        elif design == DesignType.RESULTS:
            return self.result_design

    def rename(self, new_name: str):
        endpoint = f"/api/v3/worksheet/sheet/{self.id}"

        payload = [{"attribute": "name", "operation": "update", "newValue": new_name}]

        self.session.patch(endpoint, json=payload)

        self.name = new_name
        return self

    def _reformat_formulation_addition_payload(self, response_json: dict) -> dict:
        new_dicts = []
        for item in response_json:
            this_dict = {
                "colId": item["Formulas"][0]["colId"],
                "Formulas": [
                    {
                        "formulaId": item["Formulas"][0]["formulaId"],
                        "name": item["name"],
                    }
                ],
                "name": item["name"],
                "type": item["type"],
                "session": self.session,
                "sheet": self,
            }
            new_dicts.append(this_dict)
        return new_dicts

    def add_formulation_columns(
        self,
        formulation_names: list[str],
        starting_position: dict | None = None,
    ):
        if starting_position is None:
            starting_position = {"reference_id": "COL5", "position": "rightOf"}
        sheet_id = self.id

        endpoint = f"/api/v3/worksheet/sheet/{sheet_id}/columns"

        # In case a user supplied a single formulation name instead of a list
        formulation_names = (
            formulation_names if isinstance(formulation_names, list) else [formulation_names]
        )

        payload = []
        for formulation_name in (
            formulation_names
        ):  # IS there a limit to the number I can add at once? Need to check this.
            # define payload for this item
            payload.append(
                {
                    "type": "INV",
                    "name": formulation_name,
                    "referenceId": starting_position["reference_id"],  # initially defined column
                    "position": starting_position["position"],
                }
            )

        response = self.session.post(endpoint, json=payload)

        self.grid = None
        new_dicts = self._reformat_formulation_addition_payload(response_json=response.json())
        return [Column(**x) for x in new_dicts]

    def add_blank_row(
        self,
        row_name: str,
        design: DesignType | str | None = DesignType.PRODUCTS,
        position: dict | None = None,
    ):
        if position is None:
            position = {"reference_id": "ROW1", "position": "above"}
        endpoint = f"/api/v3/worksheet/design/{self._get_design_id(design=design)}/rows"

        payload = [
            {
                "type": "BLK",
                "name": row_name,
                "referenceId": position["reference_id"],
                "position": position["position"],
            }
        ]

        response = self.session.post(endpoint, json=payload)

        self.grid = None
        row_dict = response.json()[0]
        return Row(
            rowId=row_dict["rowId"],
            type=row_dict["type"],
            session=self.session,
            design=self._get_design(design=design),
            name=row_dict["name"],
            sheet=self,
        )

    def add_inventory_row(
        self,
        inventory_id: str,
        position: dict | None = None,
    ):
        if position is None:
            position = {"reference_id": "ROW1", "position": "above"}
        design_id = self.product_design.id
        endpoint = f"/api/v3/worksheet/design/{design_id}/rows"

        payload = {
            "type": "INV",
            "id": ("INV" + inventory_id if not inventory_id.startswith("INV") else inventory_id),
            "referenceId": position["reference_id"],
            "position": position["position"],
        }

        response = self.session.post(endpoint, json=payload)

        self.grid = None
        row_dict = response.json()
        return Row(
            rowId=row_dict["rowId"],
            type=row_dict["type"],
            session=self.session,
            design=self.product_design,
            sheet=self,
            name=row_dict["name"],
            id=row_dict["id"],
            manufacturer=row_dict["manufacturer"],
        )

    def _filter_cells(self, cells: list[Cell], response_dict: dict):
        updated = []
        failed = []
        for c in cells:
            found = False
            for r in response_dict["UpdatedItems"]:
                if r["id"]["rowId"] == c.row_id and r["id"]["colId"] == c.column_id:
                    found = True
                    updated.append(c)
            if not found:
                failed.append(c)
        return (updated, failed)

    def _get_current_cell(self, cell: Cell) -> Cell:
        filtered_columns = [
            col for col in self.grid.columns if col.startswith(cell.column_id + "#")
        ]
        filtered_rows = [
            idx
            for idx in self.grid.index
            if idx.startswith(cell.design_id + "#" + cell.row_id + "#")
        ]

        first_value = None
        for row in filtered_rows:
            for col in filtered_columns:
                first_value = self.grid.loc[row, col]
                return first_value
        return first_value

    def _get_cell_changes(self, cell: Cell) -> dict:
        current_cell = self._get_current_cell(cell=cell)

        change_dict = {
            "Id": {"rowId": cell.row_id, "colId": cell.column_id},
            "data": [],
        }
        if cell.calculation != current_cell.calculation:
            if cell.calculation is None or cell.calculation == "":
                change_dict["data"].append(
                    {
                        "operation": "delete",
                        "attribute": "calculation",
                        "oldValue": current_cell.calculation,
                    }
                )
            else:
                change_dict["data"].append(
                    {
                        "operation": "update",
                        "attribute": "calculation",
                        "oldValue": current_cell.calculation,
                        "newValue": cell.calculation,
                    }
                )
        if cell.format != current_cell.format:
            if cell.format is None or cell.format == {}:
                change_dict["data"].append(
                    {
                        "operation": "delete",
                        "attribute": "cellFormat",
                        "oldValue": current_cell.format,
                    }
                )
            else:
                change_dict["data"].append(
                    {
                        "operation": "update",
                        "attribute": "cellFormat",
                        "oldValue": current_cell.format,
                        "newValue": cell.format,
                    }
                )
        if cell.value != current_cell.value and (
            cell.calculation is None or cell.calculation == ""
        ):
            if cell.value is None or cell.value == "":
                change_dict["data"].append(
                    {
                        "operation": "delete",
                        "attribute": "value",
                        "oldValue": current_cell.value,
                    }
                )
            else:
                change_dict["data"].append(
                    {
                        "operation": "update",
                        "attribute": "value",
                        "oldValue": current_cell.value,
                        "newValue": cell.value,
                    }
                )
        if change_dict["data"] == []:
            return None
        return change_dict

    def update_cells(self, cells: list[Cell]):
        request_path_dict = {}
        updated = []
        failed = []
        # sort by design ID
        for c in cells:
            if c.design_id not in request_path_dict:
                request_path_dict[c.design_id] = [c]
            else:
                request_path_dict[c.design_id].append(c)

        for design_id, cell_list in request_path_dict.items():
            payload = []
            for cell in cell_list:
                change_dict = self._get_cell_changes(cell)
                if change_dict is not None:
                    payload.append(change_dict)

            if payload == []:
                continue

            this_url = f"/api/v3/worksheet/{design_id}/values"

            response = self.session.patch(
                this_url,
                json=payload,
            )

            if response.status_code == 204:
                # They all updated
                updated.extend(cell_list)
            elif response.status_code == 206:
                # Some updated and some did not.
                cell_results = self._filter_cells(cells=cell_list, response_dict=response.json())
                updated.extend(cell_results[0])
                failed.extend(cell_results[1])
        return (updated, failed)

    def add_blank_column(self, name: str, position: dict = None):
        if position is None:
            position = {"reference_id": "COL5", "position": "rightOf"}
        endpoint = f"/api/v3/worksheet/sheet/{self.id}/columns"
        payload = [
            {
                "type": "BLK",
                "name": name,
                "referenceId": position["reference_id"],
                "position": position["position"],
            }
        ]
        response = self.session.post(endpoint, json=payload)

        data = response.json()
        data[0]["sheet"] = self
        data[0]["session"] = self.session
        self.grid = None  # reset the known grid. We could probably make this nicer later.
        return Column(**data[0])

    def delete_column(self, column_id: str):
        endpoint = f"/api/v3/worksheet/sheet/{self.id}/columns"
        payload = [{"colId": column_id}]
        self.session.delete(endpoint, json=payload)

        if self._grid is not None:  # if I have a grid loaded into memory, adjust it.
            self.grid = None
        return True

    def delete_row(self, row_id: str, design_id: str):
        endpoint = f"/api/v3/worksheet/design/{design_id}/rows"
        payload = [{"rowId": row_id}]
        self.session.delete(endpoint, json=payload)

        if self._grid is not None:  # if I have a grid loaded into memory, adjust it.
            self.grid = None
        return True

    def _find_column(self, column_id: str = "", column_name: str = ""):
        if column_id == None:
            column_id = ""
        if column_name == None:
            column_name = ""
        search_str = f"{column_id}#{column_name}"
        matches = [col for col in self.grid.columns if search_str in col]
        if len(matches) == 0:
            return None
        elif len(matches) > 1:
            raise RuntimeError(
                f"Ambiguous match on column name {column_name}. Please try provided a column ID"
            )
        else:
            return self.grid[matches[0]]

    def get_column(self, column_id: None | str = None, column_name: str | None = None):
        if column_id is None and column_name is None:
            raise RuntimeError("Either a column name or id must be provided")
        else:
            matching_series = self._find_column(column_id=column_id, column_name=column_name)
            first_item = matching_series.iloc[0]
            return Column(
                name=first_item.name,
                colId=first_item.column_id,
                type=first_item.type,
                sheet=self,
                session=self.session,
            )


class Column(BaseSessionModel):
    column_id: str = Field(alias="colId")
    formulas: list[Formulations] = Field(default=None, alias="Formulas")
    name: str
    type: CellType
    sheet: Sheet
    _cells: list[Cell] | None = PrivateAttr(default=None)

    @property
    def df_name(self):
        return f"{self.column_id}#{self.name}"

    @property
    def cells(self) -> list[Cell]:
        return self.sheet.grid[self.df_name]

    def rename(self, new_name):
        payload = {
            "data": [
                {
                    "operation": "update",
                    "attribute": "name",
                    "colId": self.column_id,
                    "oldValue": self.name,
                    "newValue": new_name,
                }
            ]
        }

        self.session.patch(
            url=f"/api/v3/worksheet/sheet/{self.sheet.id}/columns",
            json=payload,
        )

        if self.sheet._grid is not None:  # if I have a grid loaded into memory, adjust it.
            self.sheet.grid = None
            # self.sheet._grid.rename(axis=1, mapper={self.name:new_name})
        self.name = new_name
        return self

    def recolor_cells(self, color: CellColor):
        new_cells = []
        for c in self.cells:
            cell_copy = copy.deepcopy(c)
            cell_copy.format = {"bgColor": color.value}
            new_cells.append(cell_copy)
        return self.sheet.update_cells(new_cells)


class Row(BaseSessionModel):
    row_id: str = Field(alias="rowId")
    type: CellType
    design: Design
    sheet: Sheet
    name: str
    inventory_id: str | None = Field(default=None, alias="id")
    manufacturer: str | None = Field(default=None)

    @property
    def row_unique_id(self):
        return f"{self.design.id}#{self.row_id}"

    @property
    def cells(self) -> list[Cell]:
        return self.sheet.grid.loc[self.row_unique_id]

    def recolor_cells(self, color: CellColor):
        new_cells = []
        for c in self.cells:
            cell_copy = copy.deepcopy(c)
            cell_copy.format = {"bgColor": color.value}
            new_cells.append(cell_copy)
        return self.sheet.update_cells(new_cells)
