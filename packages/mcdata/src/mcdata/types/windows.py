from typing import Literal, Required, TypedDict


class Window(TypedDict, total=False):
    """window."""

    id: Required[str]
    """
    The unique identifier for the window

    Required property
    """

    name: Required[str]
    """
    The default displayed name of the window

    Required property
    """

    slots: list["_WindowSlotsItem"]
    """
    The slots displayed in the window

    minItems: 1
    uniqueItems: True
    additionalItems: False
    """

    properties: list[str]
    """
    Names of the properties of the window

    minItems: 1
    additionalItems: False
    """

    openedWith: list["_WindowOpenedwithItem"]


Windows = list["Window"]
"""
windows.

minItems: 1
uniqueItems: True
"""


class _WindowOpenedwithItem(TypedDict, total=False):
    type: Required["_WindowOpenedwithItemType"]
    """ Required property """

    id: Required[int]
    """ Required property """


_WindowOpenedwithItemType = Literal["item"] | Literal["entity"] | Literal["block"]
_WINDOWOPENEDWITHITEMTYPE_ITEM: Literal["item"] = "item"
"""The values for the '_WindowOpenedwithItemType' enum"""
_WINDOWOPENEDWITHITEMTYPE_ENTITY: Literal["entity"] = "entity"
"""The values for the '_WindowOpenedwithItemType' enum"""
_WINDOWOPENEDWITHITEMTYPE_BLOCK: Literal["block"] = "block"
"""The values for the '_WindowOpenedwithItemType' enum"""


class _WindowSlotsItem(TypedDict, total=False):
    """A slot or slot range in the window"""

    name: Required[str]
    """
    The name of the slot or slot range

    Required property
    """

    index: Required[int]
    """
    The position of the slot or begin of the slot range

    minimum: 0

    Required property
    """

    size: int
    """
    The size of the slot range

    minimum: 0
    """
