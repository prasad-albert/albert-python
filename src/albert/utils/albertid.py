def ensure_inventory_id(id: str) -> str:
    return f"INV{id}" if not id.startswith("INV") else id


def ensure_tag_id(id: str) -> str:
    return f"TAG{id}" if not id.startswith("TAG") else id
