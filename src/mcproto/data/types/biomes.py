from typing import Literal, Required, TypedDict


class Biome(TypedDict, total=False):
    """biome."""

    id: Required[int]
    """
    The unique identifier for a biome

    minimum: 0

    Required property
    """

    name: Required[str]
    """
    The name of a biome

    Required property
    """

    category: Required[str]
    """
    The category of a biome

    Required property
    """

    temperature: Required[int | float]
    """
    An indicator for the temperature in a biome

    minimum: -1
    maximum: 2

    Required property
    """

    precipitation: "_BiomePrecipitation"
    """ The type of precipitation: none, rain or snow [before 1.19.4] """

    has_precipitation: bool
    """ True if a biome has any precipitation (rain or snow) [1.19.4+] """

    dimension: Required[str]
    """
    The dimension of a biome: overworld, nether, end, or the_end (bedrock)

    Required property
    """

    displayName: Required[str]
    """
    The display name of a biome

    pattern: \\S+

    Required property
    """

    color: Required[int]
    """
    The color in a biome

    minimum: 0

    Required property
    """

    rainfall: int | float
    """
    How much rain there is in a biome [before 1.19.4]

    minimum: 0
    maximum: 1
    """

    depth: int | float
    """ The depth/height variation of the biome terrain """

    climates: list["_BiomeClimatesItem"]
    """
    Climate data for the biome

    minItems: 1
    """

    name_legacy: str
    """ Legacy name of the biome used in older versions """

    parent: str
    """ Parent biome name for variant biomes """

    child: int
    """
    Child biome ID for variant biomes

    minimum: 0
    """


Biomes = list["Biome"]
"""
biomes.

uniqueItems: True
"""


class _BiomeClimatesItem(TypedDict, total=False):
    temperature: Required[int | float]
    """
    Climate temperature value

    Required property
    """

    humidity: Required[int | float]
    """
    Climate humidity value

    Required property
    """

    altitude: Required[int | float]
    """
    Climate altitude value

    Required property
    """

    weirdness: Required[int | float]
    """
    Climate weirdness value

    Required property
    """

    offset: Required[int | float]
    """
    Climate offset value

    Required property
    """


_BiomePrecipitation = Literal["none"] | Literal["rain"] | Literal["snow"]
""" The type of precipitation: none, rain or snow [before 1.19.4] """
_BIOMEPRECIPITATION_NONE: Literal["none"] = "none"
"""The values for the 'The type of precipitation: none, rain or snow [before 1.19.4]' enum"""
_BIOMEPRECIPITATION_RAIN: Literal["rain"] = "rain"
"""The values for the 'The type of precipitation: none, rain or snow [before 1.19.4]' enum"""
_BIOMEPRECIPITATION_SNOW: Literal["snow"] = "snow"
"""The values for the 'The type of precipitation: none, rain or snow [before 1.19.4]' enum"""
