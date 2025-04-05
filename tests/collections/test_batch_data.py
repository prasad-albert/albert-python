from albert import Albert
from albert.resources.tasks import BaseTask, BatchTask


def test_get_by_id(client: Albert, seeded_tasks: list[BaseTask]):
    batch_task = [t for t in seeded_tasks if isinstance(t, BatchTask)][0]
    batch_data = client.batch_data.get(id=batch_task.id)
    assert batch_data.id == batch_task.id
