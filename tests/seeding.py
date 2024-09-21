from albert.resources.cas import Cas, CasCategory
from albert.resources.companies import Company
from albert.resources.locations import Location
from albert.resources.projects import Project, ProjectCategory, ProjectClass
from albert.resources.tags import Tag
from albert.resources.units import Unit, UnitCategory


def generate_cas_seeds() -> list[Cas]:
    """
    Generates a list of CAS seed objects for testing without IDs.

    Returns
    -------
    List[Cas]
        A list of Cas objects with different permutations.
    """

    return [
        # CAS with basic fields
        Cas(number="50-00-0", description="Formaldehyde", category=CasCategory.USER, smiles="C=O"),
        Cas(
            number="64-17-5",
            description="Ethanol",
            category=CasCategory.TSCA_PUBLIC,
            smiles="C2H5OH",
        ),
        # CAS with optional fields filled out
        Cas(
            number="7732-18-5",
            description="Water",
            notes="Common solvent",
            category=CasCategory.NOT_TSCA,
            smiles="O",
            inchi_key="XLYOFNOQVPJJNP-UHFFFAOYSA-N",
            iupac_name="Oxidane",
            name="Water",
        ),
        # CAS with external database reference
        Cas(
            number="7440-57-5",
            description="Gold",
            category=CasCategory.EXTERNAL,
            smiles="[Au]",
            inchi_key="N/A",
            iupac_name="Gold",
            name="Gold",
        ),
        # CAS with unknown classification
        Cas(number="1234-56-7", description="Unknown substance", category=CasCategory.UNKNOWN),
    ]


def generate_company_seeds() -> list[Company]:
    """
    Generates a list of Company seed objects for testing without IDs.

    Returns
    -------
    List[Company]
        A list of Company objects with different permutations.
    """

    return [
        # Basic company with name only
        Company(name="Acme Corporation"),
        # Company with a full name and additional private attribute (distance)
        Company(name="Globex Corporation"),
        # Another company
        Company(name="Initech"),
        # One more company with a distance attribute
        Company(name="Umbrella Corp"),
    ]


def generate_location_seeds() -> list[Location]:
    """
    Generates a list of Location seed objects for testing without IDs.

    Returns
    -------
    List[Location]
        A list of Location objects with different permutations.
    """

    return [
        # Basic location with required fields (name, latitude, longitude, address)
        Location(
            name="Warehouse A",
            latitude=40.7,
            longitude=-74.0,
            address="123 Warehouse St, New York, NY",
        ),
        # Location with full fields including optional country
        Location(
            name="Headquarters",
            latitude=37.8,
            longitude=-122.4,
            address="123 Market St, San Francisco, CA",
            country="US",
        ),
        # Location with required fields but without the country
        Location(
            name="Remote Office",
            latitude=48.9,
            longitude=2.4,
            address="10 Office Lane, Paris",
        ),
        # Another location with all fields
        Location(
            name="Test Site",
            latitude=51.5,
            longitude=-0.1,
            address="Test Facility, London",
            country="GB",
        ),
    ]


def generate_tag_seeds() -> list[Tag]:
    """
    Generates a list of Tag seed objects for testing without IDs.

    Returns
    -------
    List[Tag]
        A list of Tag objects with different permutations.
    """

    return [
        # INVENTORY tags
        Tag(tag="inventory-tag-1"),  # No id provided, will be set server-side
        Tag(tag="inventory-tag-2"),  # No id provided
        # COMPANY tags
        Tag(tag="company-tag-1"),  # No id provided
        Tag(tag="company-tag-2"),  # No id provided
    ]


def generate_unit_seeds() -> list[Unit]:
    """
    Generates a list of Unit seed objects for testing without IDs.

    Returns
    -------
    List[Unit]
        A list of Unit objects with different permutations.
    """

    return [
        # Basic unit with length category
        Unit(
            name="Meter",
            symbol="m",
            synonyms=["Metre"],
            category=UnitCategory.LENGTH,
            verified=True,
        ),
        # Unit with mass category
        Unit(name="Kilogram", symbol="kg", category=UnitCategory.MASS, verified=True),
        # Unit with temperature category and synonyms
        Unit(
            name="Celsius",
            symbol="°C",
            synonyms=["Centigrade"],
            category=UnitCategory.TEMPERATURE,
            verified=False,
        ),
        # Unit with energy category
        Unit(name="Joule", symbol="J", category=UnitCategory.ENERGY, verified=True),
        # Unit with volume category
        Unit(
            name="Liter",
            symbol="L",
            synonyms=["Litre"],
            category=UnitCategory.VOLUME,
            verified=True,
        ),
    ]


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
