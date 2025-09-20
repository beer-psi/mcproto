from typing import Any, Required, TypedDict


class FeatureEntry(TypedDict, total=False):
    """
    featureEntry.

    oneOf:
      - not:
          anyOf:
          - required:
            - versions
          - required:
            - values
        required:
        - version
      - not:
          anyOf:
          - required:
            - version
          - required:
            - values
        required:
        - versions
      - not:
          anyOf:
          - required:
            - version
          - required:
            - versions
        required:
        - values
    """

    name: Required[str]
    """
    The name of the feature

    pattern: .+

    Required property
    """

    description: Required[str]
    """
    The description of the feature

    pattern: .+

    Required property
    """

    version: str
    """ Single version where this feature applies """

    versions: list[str]
    """
    A tuple that describes the range of versions where this feature applies [minVersion, maxVersion]

    minItems: 2
    maxItems: 2
    additionalItems: False
    """

    values: list["VersionSpecificValue"]
    """ Version-specific values for features that have different values across versions """


Features = list["FeatureEntry"]
"""
features.

uniqueItems: True
"""


class VersionSpecificValue(TypedDict, total=False):
    """
    versionSpecificValue.

    oneOf:
      - not:
          required:
          - versions
        required:
        - version
      - not:
          required:
          - version
        required:
        - versions
    """

    value: Required[Any]  # pyright: ignore[reportExplicitAny]
    """
    The value for this feature in the specified versions

    Required property
    """

    version: str
    """ Single version where this value applies """

    versions: list[str]
    """
    Version range where this value applies [minVersion, maxVersion]

    minItems: 2
    maxItems: 2
    additionalItems: False
    """
