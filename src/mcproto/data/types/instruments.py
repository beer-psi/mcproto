from typing import Required, TypedDict


class Instrument(TypedDict, total=False):
    """instrument."""

    id: Required[int]
    """
    The unique identifier for an instrument

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of an instrument

    pattern: \\S+

    Required property
    """

    sound: str
    """
    The sound ID played by this instrument

    pattern: \\S+
    """


Instruments = list["Instrument"]
"""
instruments.

uniqueItems: True
"""
