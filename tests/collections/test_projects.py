from collections.abc import Generator

import pytest

from albert.albert import Albert
from albert.collections.projects import ProjectCollection
from albert.resources.base import BaseEntityLink
from albert.resources.projects import Project
from albert.utils.exceptions import NotFoundError


def _list_asserts(returned_list):
    found = False
    for i, project in enumerate(returned_list):
        if i == 50:  # Limit to checking first 50 projects
            break
        assert isinstance(project, Project)
        assert isinstance(project.description, str)
        assert project.id is not None
        found = True
    assert found


def test_list_projects(client: Albert):
    project_collection = ProjectCollection(session=client.session)
    project_list = project_collection.list()
    assert isinstance(project_list, Generator)
    _list_asserts(project_list)


def test_get_by_id(client: Albert, seeded_projects: list[Project]):
    project_collection = ProjectCollection(session=client.session)

    # Get the first seeded project by ID
    seeded_project = seeded_projects[0]
    fetched_project = project_collection.get_by_id(project_id=seeded_project.id)

    assert isinstance(fetched_project, Project)
    assert fetched_project.id == seeded_project.id
    assert fetched_project.description == seeded_project.description


def test_create_project(client: Albert, seeded_locations):
    project_collection = ProjectCollection(session=client.session)

    # Create a new project
    new_project = Project(
        description="A basic development project.",
        locations=[BaseEntityLink(id=seeded_locations[0].id)],
    )

    created_project = project_collection.create(project=new_project)
    assert isinstance(created_project, Project)
    assert isinstance(created_project.id, str)
    assert created_project.description == "A basic development project."

    # Clean up
    project_collection.delete(project_id=created_project.id)


def test_delete_project(client: Albert, seeded_locations):
    project_collection = ProjectCollection(session=client.session)

    # Create a new project to delete
    new_project = Project(
        description="Project to Delete",
        # acls=[],
        locations=[BaseEntityLink(id=seeded_locations[1].id)],
    )

    created_project = project_collection.create(project=new_project)
    assert isinstance(created_project, Project)

    # Now delete the project
    success = project_collection.delete(project_id=created_project.id)
    assert success

    # Try to fetch the project, should return None or not found
    with pytest.raises(NotFoundError):
        project_collection.get_by_id(project_id=created_project.id)
