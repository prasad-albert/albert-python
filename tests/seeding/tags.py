from albert.resources.tags import Tag


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
