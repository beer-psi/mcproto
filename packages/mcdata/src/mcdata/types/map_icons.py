from typing import Required, TypedDict


class MapIcon(TypedDict, total=False):
    """mapIcon."""

    id: Required[int]
    """
    The unique identifier for a map icon

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of a map icon

    Required property
    """

    appearance: str
    """ Description of the map icon's appearance """

    visibleInItemFrame: Required[bool]
    """
    Visibility in item frames

    Required property
    """


Mapicons = list["MapIcon"]
"""
mapIcons.

uniqueItems: True
"""
