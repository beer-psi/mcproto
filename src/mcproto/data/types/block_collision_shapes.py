from typing import Required, TypedDict, Union


class BlockCollisionShapes(TypedDict, total=False):
    """blockCollisionShapes."""

    blocks: Required[dict[str, "_BlockcollisionshapesBlocksAdditionalproperties"]]
    """
    Each block's collision shape id(s).

    Required property
    """

    shapes: Required[dict[str, "_BlockcollisionshapesShapesAdditionalproperties"]]
    """
    Collision shapes by id, each shape being composed of a list of collision boxes.

    Required property
    """


_BlockcollisionshapesBlocksAdditionalproperties = Union[
    "_BlockcollisionshapesBlocksAdditionalpropertiesOneof0",
    "_BlockcollisionshapesBlocksAdditionalpropertiesOneof1",
]
""" Aggregation type: oneOf """


_BlockcollisionshapesBlocksAdditionalpropertiesOneof0 = int | float
"""
The shape id shared by all block states of this block.

minimum: 0
"""


_BlockcollisionshapesBlocksAdditionalpropertiesOneof1 = list[
    "_BlockcollisionshapesBlocksAdditionalpropertiesOneof1Item"
]
"""
The shape ids of each block state of this block.

minItems: 1
"""


_BlockcollisionshapesBlocksAdditionalpropertiesOneof1Item = int | float
""" minimum: 0 """


_BlockcollisionshapesShapesAdditionalproperties = list[
    "_BlockcollisionshapesShapesAdditionalpropertiesItem"
]
""" The boxes of this shape. """


_BlockcollisionshapesShapesAdditionalpropertiesItem = list[
    "_BlockcollisionshapesShapesAdditionalpropertiesItemItem"
]
"""
The min/max x/y/z corner coordinates of this box.

minItems: 6
maxItems: 6
"""


_BlockcollisionshapesShapesAdditionalpropertiesItemItem = int | float
"""
minimum: -0.25
maximum: 1.5
"""
