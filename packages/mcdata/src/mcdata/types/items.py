from typing import Required, TypedDict


class Item(TypedDict, total=False):
    """item."""

    id: Required[int]
    """
    The unique identifier for an item

    minimum: 0

    Required property
    """

    displayName: Required[str]
    """
    The display name of an item

    Required property
    """

    stackSize: Required[int]
    """
    Stack size for an item

    minimum: 0

    Required property
    """

    enchantCategories: list[str]
    """
    describes categories of enchants this item can use

    uniqueItems: True
    """

    repairWith: list[str]
    """
    describes what items this item can be fixed with in an anvil

    uniqueItems: True
    """

    maxDurability: int
    """
    the amount of durability an item has before being damaged/used

    minimum: 0
    """

    durability: int
    """
    durability value for editions that specify it alongside maxDurability

    minimum: 0
    """

    metadata: int
    """
    legacy data value used in some editions at the item level

    minimum: 0
    """

    name: Required[str]
    """
    The name of an item

    pattern: \\S+

    Required property
    """

    blockStateId: int
    """
    Block state id associated with this item in some editions

    minimum: 0
    """

    variations: list["_ItemVariationsItem"]


Items = list["Item"]
"""
items.

uniqueItems: True
"""


class _ItemVariationsItem(TypedDict, total=False):
    metadata: Required[int]
    """
    minimum: 0

    Required property
    """

    displayName: Required[str]
    """ Required property """

    id: int
    """
    The unique identifier for a variation (when applicable)

    minimum: 0
    """

    name: str
    """
    The name of a variation (when applicable)

    pattern: \\S+
    """

    stackSize: int
    """
    Stack size for a variation (when applicable)

    minimum: 0
    """

    enchantCategories: list[str]
    """
    describes categories of enchants this variation can use

    uniqueItems: True
    """
