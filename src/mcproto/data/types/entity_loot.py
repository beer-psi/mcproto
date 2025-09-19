from typing import Required, TypedDict


class EntityItemDrop(TypedDict, total=False):
    """entityItemDrop."""

    item: Required[str]
    """
    The name of the item being dropped

    Required property
    """

    metadata: int
    """
    The metadata of the item being dropped (Bedrock Edition)

    minimum: 0
    maximum: 127
    """

    dropChance: Required[int | float]
    """
    The percent chance of the item drop to occur

    Required property
    """

    stackSizeRange: Required[list[int | float | None]]
    """
    The min/max of number of items in this item drop stack

    Required property
    """

    playerKill: bool
    """ If a player killer is required """


EntityLoot = list["EntityLootEntry"]
"""
entityLoot.

uniqueItems: True
"""


class EntityLootEntry(TypedDict, total=False):
    """entityLootEntry."""

    entity: Required[str]
    """
    The name of the entity

    pattern: \\S+

    Required property
    """

    drops: Required[list["EntityItemDrop"]]
    """
    The list of item drops

    uniqueItems: True

    Required property
    """
