from typing import Any, Required, TypedDict

BlockMappings = list["BlockMappingItem"]
"""
blockMappings.

Maps block names and states between PC and PE (Bedrock) versions.
"""


class BlockMappingItem(TypedDict, total=False):
    """A mapping between a PC and PE block."""

    pc: Required["BlockReference"]
    """
    A reference to a block, including its name and states.

    Required property
    """

    pe: Required["BlockReference"]
    """
    A reference to a block, including its name and states.

    Required property
    """


class BlockReference(TypedDict, total=False):
    """A reference to a block, including its name and states."""

    name: Required[str]
    """
    The block's unique name identifier.

    Required property
    """

    states: Required[dict[str, Any]]  # pyright: ignore[reportExplicitAny]
    """
    The block's state properties as key-value pairs.

    Required property
    """
