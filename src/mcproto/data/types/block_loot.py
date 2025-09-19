from typing import Any, Required, TypedDict


class BlockItemDrop(TypedDict, total=False):
    """blockItemDrop."""

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

    blockAge: int | float
    """ The required age of the block for the item drop to occur """

    silkTouch: bool
    """ If silk touch is required """

    noSilkTouch: bool
    """ If not having silk touch is required """


BlockLoot = list["BlockLootEntry"]
"""
blockLoot.

uniqueItems: True
"""


class BlockLootEntry(TypedDict, total=False):
    """blockLootEntry."""

    block: Required[str]
    """
    The name of the block

    pattern: \\S+

    Required property
    """

    states: dict[str, Any]
    """ The states of the block (Bedrock Edition) """

    drops: Required[list["BlockItemDrop"]]
    """
    The list of item drops

    uniqueItems: True

    Required property
    """
