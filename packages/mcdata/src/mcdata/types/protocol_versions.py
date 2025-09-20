from typing import Required, TypedDict

ProtocolVersions = list["ProtocolVersion"]
"""
protocolVersions.

uniqueItems: True
"""


class ProtocolVersion(TypedDict, total=False):
    """uniqueItems: True"""

    version: Required[int]
    """
    The protocol version

    Required property
    """

    dataVersion: int
    minecraftVersion: Required[str]
    """
    pattern: ([0-9]+\\.[0-9]+(\\.[0-9]+)?[a-z]?(-pre[0-9]+)?)|([0-9]{2}w[0-9]{2}[a-z])

    Required property
    """

    majorVersion: Required[str]
    """
    pattern: [0-9]+\\.[0-9]+[a-z]?

    Required property
    """

    usesNetty: bool
    releaseType: str
    """ pattern: [a-z]+ """
