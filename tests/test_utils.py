import uuid


def random_name(name: str | None = None) -> str:
    if name:
        return f"TEST {name} - {uuid.uuid4()}"
    else:
        return f"TEST - {uuid.uuid4()}"
