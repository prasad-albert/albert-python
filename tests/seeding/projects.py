import pytest

from albert import Albert
from albert.resources.companies import Company
from albert.resources.projects import Project, ProjectCategory, ProjectClass
from albert.resources.tags import Tag
from tests.seeding.companies import seeded_companies
from tests.seeding.tags import seeded_tags

@pytest.fixture(scope="module")
def client():
    return Albert()


def generate_project_seeds(
    seeded_tags: list[Tag], seeded_companies: list[Company]
) -> list[Project]:
    """
    Generates a list of Project seed objects for testing without IDs,
    using seeded tags and companies.

    Parameters
    ----------
    seeded_tags : List[Tag]
        List of seeded Tag objects.
    seeded_companies : List[Company]
        List of seeded Company objects.

    Returns
    -------
    List[Project]
        A list of Project objects with different permutations.
    """

    return [
        # Basic project with default class (PUBLIC) using seeded tag and company
        Project(
            name="Project Alpha",
            description="A development project.",
            category=ProjectCategory.DEVELOPMENT,
            tags=[seeded_tags[0]],
            company=seeded_companies[0],
        ),
        # Project with a specific class (CONFIDENTIAL) using multiple seeded tags and company
        Project(
            name="Project Beta",
            description="A confidential research project.",
            category=ProjectCategory.RESEARCH,
            project_class=ProjectClass.CONFIDENTIAL,
            tags=[seeded_tags[1], seeded_tags[2]],
            company=seeded_companies[1],
        ),
        # Another project with production category and default class (PUBLIC)
        Project(
            name="Project Gamma",
            description="A production project.",
            category=ProjectCategory.PRODUCTION,
            tags=[seeded_tags[3]],
            company=seeded_companies[2],
        ),
        # Project with no tags and explicit class (PRIVATE)
        Project(
            name="Project Delta",
            description="A private research project.",
            category=ProjectCategory.RESEARCH,
            project_class=ProjectClass.PRIVATE,
            company=seeded_companies[3],
        ),
    ]


@pytest.fixture(scope="function")
def seeded_projects(client: Albert, seeded_tags, seeded_companies):
    """
    Fixture to seed projects before the test and delete them after,
    using seeded tags and companies.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.
    seeded_tags : List[Tag]
        The list of seeded Tag objects.
    seeded_companies : List[Company]
        The list of seeded Company objects.

    Returns
    -------
    List[Project]
        The list of seeded Project objects.
    """
    # Seed the projects using seeded tags and companies
    seeded = []
    for project in generate_project_seeds(
        seeded_tags=seeded_tags, seeded_companies=seeded_companies
    ):
        created_project = client.projects.create(project=project)
        seeded.append(created_project)

    yield seeded  # Provide the seeded projects to the test

    # Teardown - delete the seeded projects after the test
    for project in seeded:
        client.projects.delete(project_id=project.id)
