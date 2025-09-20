# pyright: reportDeprecated=false
from typing import Literal, Required, TypedDict, Union


class Block(TypedDict, total=False):
    """block."""

    id: Required[int]
    """
    The unique identifier for a block

    minimum: 0

    Required property
    """

    displayName: Required[str]
    """
    The display name of a block

    Required property
    """

    name: Required[str]
    """
    The name of a block

    pattern: \\S+

    Required property
    """

    hardness: Required[int | float | None]
    """
    Hardness of a block

    minimum: -1

    Required property
    """

    stackSize: Required[int]
    """
    Stack size for a block

    minimum: 0

    Required property
    """

    diggable: Required[bool]
    """
    true if a block is diggable

    Required property
    """

    boundingBox: Required["_BlockBoundingbox"]
    """
    BoundingBox of a block

    Required property
    """

    material: str
    """ Material of a block """

    harvestTools: dict[str, bool]
    """ Using one of these tools is required to harvest a block, without that you get a 3.33x time penalty. """

    variations: list["_BlockVariationsItem"]
    states: list["_BlockStatesItem"]
    drops: Required[list["_BlockDropsItem"]]
    """ Required property """

    transparent: Required[bool]
    """
    true if a block is transparent

    Required property
    """

    emitLight: Required[int]
    """
    Light emitted by that block

    minimum: 0
    maximum: 15

    Required property
    """

    filterLight: Required[int]
    """
    Light filtered by that block

    minimum: 0
    maximum: 15

    Required property
    """

    minStateId: int
    """
    Minimum state id

    minimum: 0
    """

    maxStateId: int
    """
    Maximum state id

    minimum: 0
    """

    defaultState: int
    """
    Default state id

    minimum: 0
    """

    resistance: int | float | None
    """
    Blast resistance

    minimum: -1
    """


Blocks = list["Block"]
"""
blocks.

uniqueItems: True
"""


_BlockBoundingbox = Literal["block"] | Literal["empty"]
""" BoundingBox of a block """
_BLOCKBOUNDINGBOX_BLOCK: Literal["block"] = "block"
"""The values for the 'BoundingBox of a block' enum"""
_BLOCKBOUNDINGBOX_EMPTY: Literal["empty"] = "empty"
"""The values for the 'BoundingBox of a block' enum"""


_BlockDropsItem = Union[int, "_BlockDropsItemOneof1"]
""" Aggregation type: oneOf """


class _BlockDropsItemOneof1(TypedDict, total=False):
    minCount: int | float
    """
    minimum number or chance, default : 1

    minimum: 0
    """

    maxCount: int | float
    """
    maximum number or chance, default : minCount

    minimum: 0
    """

    drop: Required[Union[int, "_BlockDropsItemOneof1DropOneof1"]]
    """
    Aggregation type: oneOf

    Required property
    """


class _BlockDropsItemOneof1DropOneof1(TypedDict, total=False):
    id: Required[int]
    """
    minimum: 0

    Required property
    """

    metadata: Required[int]
    """
    minimum: 0

    Required property
    """


class _BlockStatesItem(TypedDict, total=False):
    name: Required[str]
    """
    The name of the property

    Required property
    """

    type: Required["_BlockStatesItemType"]
    """
    The type of the property

    Required property
    """

    values: None
    """
    The possible values of the property

    WARNING: we get an array without any items
    """

    num_values: Required[int | float]
    """
    The number of possible values

    minimum: 1

    Required property
    """


_BlockStatesItemType = (
    Literal["enum"] | Literal["bool"] | Literal["int"] | Literal["direction"]
)
""" The type of the property """
_BLOCKSTATESITEMTYPE_ENUM: Literal["enum"] = "enum"
"""The values for the 'The type of the property' enum"""
_BLOCKSTATESITEMTYPE_BOOL: Literal["bool"] = "bool"
"""The values for the 'The type of the property' enum"""
_BLOCKSTATESITEMTYPE_INT: Literal["int"] = "int"
"""The values for the 'The type of the property' enum"""
_BLOCKSTATESITEMTYPE_DIRECTION: Literal["direction"] = "direction"
"""The values for the 'The type of the property' enum"""


class _BlockVariationsItem(TypedDict, total=False):
    metadata: Required[int]
    """
    minimum: 0

    Required property
    """

    displayName: Required[str]
    """ Required property """

    description: str
