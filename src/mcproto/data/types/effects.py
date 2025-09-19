from typing import Literal, Required, TypedDict


class Effect(TypedDict, total=False):
    """effect."""

    id: Required[int]
    """
    The unique identifier for an effect

    minimum: 0

    Required property
    """

    displayName: Required[str]
    """
    The display name of an effect

    Required property
    """

    name: Required[str]
    """
    The name of an effect

    pattern: \\S+

    Required property
    """

    type: Required["_EffectType"]
    """
    Whether an effect is positive or negative

    Required property
    """


Effects = list["Effect"]
"""
effects.

uniqueItems: True
"""


_EffectType = Literal["good"] | Literal["bad"]
""" Whether an effect is positive or negative """
_EFFECTTYPE_GOOD: Literal["good"] = "good"
"""The values for the 'Whether an effect is positive or negative' enum"""
_EFFECTTYPE_BAD: Literal["bad"] = "bad"
"""The values for the 'Whether an effect is positive or negative' enum"""
