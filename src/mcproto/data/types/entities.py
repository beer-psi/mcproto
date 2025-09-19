from typing import Required, TypedDict

Entities = list["Entity"]
"""
entities.

uniqueItems: True
"""


class Entity(TypedDict, total=False):
    """entity."""

    id: Required[int]
    """
    The unique identifier for an entity

    minimum: 0

    Required property
    """

    internalId: int
    """
    The internal id of an entity : used in eggs metadata for example

    minimum: 0
    """

    displayName: Required[str]
    """
    The display name of an entity

    Required property
    """

    name: Required[str]
    """
    The name of an entity

    pattern: \\S+

    Required property
    """

    type: Required[str]
    """
    The type of an entity

    Required property
    """

    width: Required[int | float | None]
    """
    The width of the entity

    Required property
    """

    height: Required[int | float | None]
    """
    The height of the entity

    Required property
    """

    length: int | float | None
    """ The length of the entity """

    offset: int | float | None
    """ The offset of the entity """

    category: str
    """ The category of an entity : a semantic category """

    metadataKeys: list[str]
    """ The pc metadata tags of an entity. (Naming is via mc code, with data_ and id_ prefixes stripped) """
