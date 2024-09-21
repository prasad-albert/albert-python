from albert.resources.companies import Company
from albert.resources.projects import Project, ProjectCategory, ProjectClass
from albert.resources.tags import Tag


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
