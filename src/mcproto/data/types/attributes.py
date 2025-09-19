from typing import Required, TypedDict


class Attribute(TypedDict, total=False):
    """attribute."""

    resource: Required[str]
    """
    The Mojang name of an attribute (usually is generic.[name] or minecraft:generic.[name]

    Required property
    """

    name: Required[str]
    """
    The name of an attribute

    pattern: \\S+

    Required property
    """

    min: Required[int | float]
    """
    The minimum value of an attribute

    Required property
    """

    max: Required[int | float]
    """
    The maximum value of an attribute

    Required property
    """

    default: Required[int | float]
    """
    The default value of an attribute

    Required property
    """


Attributes = list["Attribute"]
"""
attributes.

uniqueItems: True
"""
