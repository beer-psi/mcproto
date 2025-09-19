from typing import Required, TypedDict


class Particle(TypedDict, total=False):
    """particle."""

    id: Required[int]
    """
    The unique identifier for a particle

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of a particle

    pattern: \\S+

    Required property
    """


Particles = list["Particle"]
"""
particles.

uniqueItems: True
"""
