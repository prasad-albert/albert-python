from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.projects import ProjectCollection
from albert.resources.projects import Project
from tests.seeding.projects import seeded_projects

@pytest.fixture(scope="module")
def client():
    return Albert()


def _list_asserts(returned_list):
    found = False
    for i, project in enumerate(returned_list):
        if i == 50:  # Limit to checking first 50 projects
            break
        assert isinstance(project, Project)
        assert isinstance(project.name, str)
        assert project.id is not None
        found = True
    assert found


def test_list_projects(client: Albert, seeded_projects):
    project_collection = ProjectCollection(session=client.session)
    project_list = project_collection.list()
    assert isinstance(project_list, Generator)
    _list_asserts(project_list)


def test_get_by_id(client: Albert, seeded_projects):
    project_collection = ProjectCollection(session=client.session)

    # Get the first seeded project by ID
    seeded_project = seeded_projects[0]
    fetched_project = project_collection.get_by_id(project_id=seeded_project.id)

    assert isinstance(fetched_project, Project)
    assert fetched_project.id == seeded_project.id
    assert fetched_project.name == seeded_project.name


def test_create_project(client: Albert):
    project_collection = ProjectCollection(session=client.session)

    # Create a new project
    new_project = Project(
        name="New Project",
        description="A new development project.",
        category="Development",
        tags=[],
        company=None,
    )

    created_project = project_collection.create(project=new_project)
    assert isinstance(created_project, Project)
    assert created_project.name == "New Project"
    assert created_project.description == "A new development project."

    # Clean up
    project_collection.delete(project_id=created_project.id)


def test_update_project(client: Albert, seeded_projects):
    project_collection = ProjectCollection(session=client.session)

    # Update the first seeded project
    seeded_project = seeded_projects[0]
    updated_data = {"name": "Updated Project Name", "description": "An updated description."}

    success = project_collection.update(project_id=seeded_project.id, patch_data=updated_data)
    assert success

    # Retrieve updated project to confirm changes
    updated_project = project_collection.get_by_id(project_id=seeded_project.id)
    assert updated_project.name == "Updated Project Name"
    assert updated_project.description == "An updated description."


def test_delete_project(client: Albert):
    project_collection = ProjectCollection(session=client.session)

    # Create a new project to delete
    new_project = Project(
        name="Project to Delete",
        description="A project to be deleted.",
        category="Development",
        tags=[],
        company=None,
    )

    created_project = project_collection.create(project=new_project)
    assert isinstance(created_project, Project)

    # Now delete the project
    success = project_collection.delete(project_id=created_project.id)
    assert success

    # Try to fetch the project, should return None or not found
    deleted_project = project_collection.get_by_id(project_id=created_project.id)
    assert deleted_project is None
