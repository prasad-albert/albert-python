from albert.resources.base import BaseEntityLink
from albert.resources.cas import Cas, CasCategory
from albert.resources.companies import Company
from albert.resources.locations import Location
from albert.resources.projects import GridDefault, Metadata, Project, ProjectClass
from albert.resources.tags import Tag
from albert.resources.units import Unit, UnitCategory


def generate_project_seeds(seeded_locations: list[Location]) -> list[Project]:
    """
    Generates a list of Project seed objects for testing without IDs.

    Parameters
    ----------
    seeded_locations : List[Location]
        List of seeded Location objects.

    Returns
    -------
    List[Project]
        A list of Project objects with different permutations.
    """

    return [
        # Project with basic metadata and public classification
        Project(
            description="A basic development project.",
            locations=[BaseEntityLink(id=seeded_locations[0].id)],
            project_class=ProjectClass.PRIVATE,
            metadata=Metadata(
                adpNumber="adp123",
            ),
        ),
        # Project with shared classification and advanced metadata
        Project(
            description="A research project focused on new materials.",
            locations=[BaseEntityLink(id=seeded_locations[1].id)],
            project_class=ProjectClass.PRIVATE,
            grid=GridDefault.WKS,
        ),
        # Project with production category and custom ACLs
        Project(
            description="A production project with custom ACLs.",
            locations=[
                BaseEntityLink(id=seeded_locations[0].id),
                BaseEntityLink(id=seeded_locations[2].id),
            ],
            project_class=ProjectClass.CONFIDENTIAL,
        ),
    ]


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
