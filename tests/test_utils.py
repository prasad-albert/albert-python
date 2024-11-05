import uuid


def random_name() -> str:
    return f"TEST - {uuid.uuid4()}"
