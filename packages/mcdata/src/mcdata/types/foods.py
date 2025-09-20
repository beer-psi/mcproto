from typing import Required, TypedDict


class Food(TypedDict, total=False):
    """food."""

    id: Required[int]
    """
    The associated item ID for this food item

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

    name: Required[str]
    """
    The name of an item

    pattern: \\S+

    Required property
    """

    foodPoints: Required[int | float]
    """
    The amount of food points the food item replenishes

    minimum: 0

    Required property
    """

    saturation: Required[int | float]
    """
    The amount of saturation points the food restores (foodPoints * saturationRatio)

    minimum: 0

    Required property
    """

    effectiveQuality: Required[int | float]
    """
    foodPoints + saturation

    minimum: 0

    Required property
    """

    saturationRatio: Required[int | float]
    """
    The 'saturation modifier' in Minecraft code, used to determine how much saturation an item has

    minimum: 0

    Required property
    """

    variations: list["_FoodVariationsItem"]


Foods = list["Food"]
"""
foods.

uniqueItems: True
"""


class _FoodVariationsItem(TypedDict, total=False):
    metadata: Required[int]
    """
    minimum: 0

    Required property
    """

    displayName: Required[str]
    """ Required property """
