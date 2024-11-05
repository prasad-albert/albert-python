from albert import Albert
from albert.resources.tasks import BaseTask


def test_task_list(seeded_tasks, client: Albert):
    tasks = client.tasks.list()
    for task in tasks:
        assert isinstance(task, BaseTask)


def test_get_by_id(seeded_tasks, client: Albert):
    task = client.tasks.get_by_id(task_id=seeded_tasks[0].id)
    assert isinstance(task, BaseTask)
    assert task.id == seeded_tasks[0].id
    assert task.name == seeded_tasks[0].name
