import pytest

from albert import Albert
from albert.resources.tags import Tag


@pytest.fixture(scope="module")
def client():
    return Albert()


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


# Example usage within a pytest fixture
@pytest.fixture(scope="function")
def seeded_tags(client: Albert):
    """
    Fixture to seed tags before the test and delete them after.

    Parameters
    ----------
    client : Albert
        The Albert SDK client instance.

    Returns
    -------
    List[Tag]
        The list of seeded Tag objects.
    """
    # Seed the tags
    seeded = []
    for tag in generate_tag_seeds():
        created_tag = client.tags.create(tag=tag)
        seeded.append(created_tag)

    yield seeded  # Provide the seeded tags to the test

    # Teardown - delete the seeded tags after the test
    for tag in seeded:
        client.tags.delete(tag_id=tag.id)
