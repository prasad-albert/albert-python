from albert.resources.base import BaseEntityLink
from albert.resources.cas import Cas, CasCategory
from albert.resources.companies import Company
from albert.resources.locations import Location

# from albert.resources.lots import Lot, LotMetadata, LotStatus
from albert.resources.projects import GridDefault, Metadata, Project, ProjectClass
from albert.resources.roles import Role
from albert.resources.tags import Tag
from albert.resources.units import Unit, UnitCategory
from albert.resources.users import User, UserClass, UserMetadata


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
        Cas(
            number="TEST-50-00-0",
            description="Formaldehyde",
            category=CasCategory.USER,
            smiles="C=O",
        ),
        Cas(
            number="TEST-64-17-5",
            description="Ethanol",
            category=CasCategory.TSCA_PUBLIC,
            smiles="C2H5OH",
        ),
        # CAS with optional fields filled out
        Cas(
            number="TEST-7732-18-5",
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
            number="TEST-7440-57-5",
            description="Gold",
            category=CasCategory.EXTERNAL,
            smiles="[Au]",
            inchi_key="N/A",
            iupac_name="Gold",
            name="Gold",
        ),
        # CAS with unknown classification
        Cas(
            number="TEST-1234-56-7", description="Unknown substance", category=CasCategory.UNKNOWN
        ),
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
            description="A public research project focused on new materials.",
            locations=[BaseEntityLink(id=seeded_locations[1].id)],
            project_class=ProjectClass.PUBLIC,
            grid=GridDefault.WKS,
        ),
        # Project with production category and custom ACLs
        Project(
            description="A private production project",
            locations=[
                BaseEntityLink(id=seeded_locations[0].id),
                BaseEntityLink(id=seeded_locations[1].id),
            ],
            project_class=ProjectClass.PRIVATE,
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
        Tag(tag="TEST-TAG-inventory-tag-1"),
        Tag(tag="TEST-TAG-inventory-tag-2"),
        Tag(tag="TEST-TAG-company-tag-1"),
        Tag(tag="TEST-TAG-company-tag-2"),
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


def generate_user_seeds(seeded_locations: list[Location], seeded_roles: list[Role]) -> list[User]:
    """
    Generates a list of User seed objects for testing without IDs.

    Parameters
    ----------
    seeded_locations : List[Location]
        List of seeded Location objects.
    seeded_roles : List[Role]
        List of seeded Role objects.

    Returns
    -------
    List[User]
        A list of User objects with different permutations.
    """

    return [
        # Basic standard user with metadata and one role
        User(
            name="Alice Smith",
            location=seeded_locations[0],
            email="testcase_alice.smith@example.com",
            roles=[seeded_roles[0]],
            user_class=UserClass.STANDARD,
            metadata=UserMetadata(sbu="SBU1"),
        ),
        # Privileged user with no metadata
        User(
            name="Bob Johnson",
            location=seeded_locations[1],
            email="testcase_bob.johnson@example.com",
            roles=[seeded_roles[0]],
            user_class=UserClass.STANDARD,
        ),
        # Admin user with full metadata
        User(
            name="Charlie Brown",
            location=seeded_locations[2],
            email="testcase_charlie.brown@example.com",
            roles=[seeded_roles[0]],
            user_class=UserClass.STANDARD,
            metadata=UserMetadata(sbu="SBU2"),
        ),
    ]


# def generate_lot_seeds(seeded_locations: list[Location], seeded_inventory:list[Inventory]) -> list[Lot]:
#     """
#     Generates a list of Lot seed objects for testing without IDs.

#     Returns
#     -------
#     List[Lot]
#         A list of Lot objects with different permutations.
#     """

#     return [
#         # Basic Lot with metadata and default status
#         Lot(
#             inventory_id="INV123",
#             storage_location=BaseEntityLink(id=seeded_stroage_locations[0].id),
#             initial_quantity=100.0,
#             cost=50.0,
#             inventory_on_hand=90.0,
#             lot_number="LOT001",
#             expiration_date="2025-12-31",
#             manufacturer_lot_number="MLN12345",
#             location=BaseEntityLink(id=seeded_locations[1].id),
#             metadata=LotMetadata(
#                 asset_tag="ASSET001",
#                 serial_number="SN123",
#                 quality_number="QN123",
#                 distributor="Distributor A",
#             ),
#             notes="This is a test lot with default status.",
#             external_barcode_id="EXT123456",
#         ),
#         # Lot with active status and no metadata
#         Lot(
#             inventory_id="INV456",
#             storage_location=BaseEntityLink(id=seeded_stroage_locations[1].id),
#             initial_quantity=500.0,
#             cost=200.0,
#             inventory_on_hand=400.0,
#             lot_number="LOT002",
#             expiration_date="2026-01-31",
#             manufacturer_lot_number="MLN67890",
#             location=BaseEntityLink(id=seeded_locations[0].id),
#             notes="This is an active lot with no metadata.",
#             external_barcode_id="EXT654321",
#             _status=LotStatus.ACTIVE,
#         ),
#         # Lot with quarantined status and full metadata
#         Lot(
#             inventory_id="INV789",
#             storage_location=BaseEntityLink(id=seeded_stroage_locations[1].id),
#             initial_quantity=1000.0,
#             cost=750.0,
#             inventory_on_hand=1000.0,
#             lot_number="LOT003",
#             expiration_date="2024-11-30",
#             manufacturer_lot_number="MLN112233",
#             location=BaseEntityLink(id=seeded_locations[1].id),
#             metadata=LotMetadata(
#                 asset_tag="ASSET789",
#                 serial_number="SN789",
#                 quality_number="QN789",
#                 distributor="Distributor B",
#             ),
#             notes="This lot is quarantined due to quality issues.",
#             external_barcode_id="EXT789012",
#             _status=LotStatus.QUARANTINED,
#         ),
#     ]
