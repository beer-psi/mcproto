from typing import Required, TypedDict


class Enchantment(TypedDict, total=False):
    """enchantment."""

    id: Required[int]
    """
    The unique identifier for an enchantment

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of an enchantment

    pattern: \\S+

    Required property
    """

    displayName: Required[str]
    """
    The display name of an enchantment

    Required property
    """

    maxLevel: Required[int]
    """
    The maximum level of an enchantment

    minimum: 1
    maximum: 5

    Required property
    """

    minCost: Required["_EnchantmentMincost"]
    """
    Min cost equation's coefficients a * level + b

    Required property
    """

    maxCost: Required["_EnchantmentMaxcost"]
    """
    Max cost equation's coefficients a * level + b

    Required property
    """

    treasureOnly: Required[bool]
    """
    Can only be found in a treasure, not created

    Required property
    """

    curse: Required[bool]
    """
    Is a curse, not an enchantment

    Required property
    """

    exclude: Required[list[str]]
    """
    List of enchantment not compatibles

    uniqueItems: True

    Required property
    """

    category: Required[str]
    """
    The category of enchantable items

    Required property
    """

    weight: Required[int]
    """
    Weight of the rarity of the enchantment

    minimum: 1
    maximum: 10

    Required property
    """

    tradeable: Required[bool]
    """
    Can this enchantment be traded

    Required property
    """

    discoverable: Required[bool]
    """
    Can this enchantment be discovered

    Required property
    """


Enchantments = list["Enchantment"]
"""
enchantments.

uniqueItems: True
"""


class _EnchantmentMaxcost(TypedDict, total=False):
    """Max cost equation's coefficients a * level + b"""

    a: int
    b: int


class _EnchantmentMincost(TypedDict, total=False):
    """Min cost equation's coefficients a * level + b"""

    a: int
    b: int
