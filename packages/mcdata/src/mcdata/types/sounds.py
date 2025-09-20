from typing import Required, TypedDict


class Sound(TypedDict, total=False):
    """ sound. """

    id: Required[int]
    """
    The unique identifier for a sound

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of a sound

    Required property
    """



Sounds = list["Sound"]
"""
sounds.

uniqueItems: True
"""

