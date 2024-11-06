import uuid


def random_name(type: str | None = None) -> str:
    if type:
        return f"TEST {type} - {uuid.uuid4()}"
    else:
        return f"TEST - {uuid.uuid4()}"
