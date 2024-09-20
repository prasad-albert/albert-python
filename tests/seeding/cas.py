import pytest

from albert import Albert
from albert.resources.cas import Cas, CasCategory  # Ensure you're importing the correct Cas model


@pytest.fixture(scope="module")
def client():
    return Albert()


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


# Example usage within a pytest fixture
@pytest.fixture(scope="function")
def seeded_cas(client: Albert):
    """
    Fixture to seed CAS before the test and delete them after.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.

    Returns
    -------
    List[Cas]
        The list of seeded Cas objects.
    """
    # Seed the CAS
    seeded = []
    for cas in generate_cas_seeds():
        created_cas = client.cas_numbers.create(cas=cas)
        seeded.append(created_cas)

    yield seeded  # Provide the seeded CAS to the test

    # Teardown - delete the seeded CAS after the test
    for cas in seeded:
        client.cas_numbers.delete(cas_id=cas.id)
